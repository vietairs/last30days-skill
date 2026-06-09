"""Security tests for the ScrapeCreators device-auth helper."""

from __future__ import annotations

import importlib.util
import stat
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "last30days"
    / "scripts"
    / "test_device_auth.py"
)
DOTENV_NAME = "." + "env"


def _load_device_auth_module():
    spec = importlib.util.spec_from_file_location("device_auth_helper", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _patch_success_flow(monkeypatch, module, *, api_key: str | None = "sc_dummy_secret_key"):
    def fake_post(url, data=None):
        if url.endswith("/code"):
            return {
                "device_code": "device_dummy",
                "user_code": "ABCD-1234",
                "verification_uri": "https://example.test/device",
                "interval": 0,
                "expires_in": 30,
            }
        if url.endswith("/token"):
            return {"access_token": "gho_dummy_secret_access_token"}
        raise AssertionError(f"unexpected POST {url}")

    def fake_get(url, token):
        assert token == "gho_dummy_secret_access_token"
        profile = {"github_username": "octo", "plan": "free"}
        if api_key is not None:
            profile["api_key"] = api_key
        return profile

    monkeypatch.setattr(module, "_post", fake_post)
    monkeypatch.setattr(module, "_get", fake_get)
    monkeypatch.setattr(module.webbrowser, "open", lambda _url: True)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)


def test_device_auth_writes_key_without_printing_secrets(monkeypatch, tmp_path, capsys):
    module = _load_device_auth_module()
    env_path = tmp_path / "last30days" / DOTENV_NAME
    _patch_success_flow(monkeypatch, module)

    module.main(config_path=env_path)

    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "gho_dummy_secret_access_token" not in output
    assert "gho_dummy_se" not in output
    assert "sc_dummy_secret_key" not in output
    assert "echo 'SCRAPECREATORS_API_KEY=" not in output
    assert "Profile response" not in output

    assert env_path.read_text(encoding="utf-8") == "SCRAPECREATORS_API_KEY=sc_dummy_secret_key\n"
    assert stat.S_IMODE(env_path.stat().st_mode) == 0o600


def test_device_auth_missing_api_key_does_not_write_or_dump_profile(monkeypatch, tmp_path, capsys):
    module = _load_device_auth_module()
    env_path = tmp_path / DOTENV_NAME
    _patch_success_flow(monkeypatch, module, api_key=None)

    with pytest.raises(SystemExit) as exc:
        module.main(config_path=env_path)

    assert exc.value.code == 1
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "github_username" in output
    assert "api_key" not in output
    assert "sc_dummy_secret_key" not in output
    assert not env_path.exists()


def test_device_auth_profile_failure_withholds_token(monkeypatch, tmp_path, capsys):
    module = _load_device_auth_module()
    env_path = tmp_path / DOTENV_NAME
    _patch_success_flow(monkeypatch, module)

    def failing_get(_url, _token):
        raise module.URLError("network down")

    monkeypatch.setattr(module, "_get", failing_get)

    with pytest.raises(SystemExit) as exc:
        module.main(config_path=env_path)

    assert exc.value.code == 1
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "gho_dummy_secret_access_token" not in output
    assert "token withheld" in output
    assert not env_path.exists()


def test_upsert_env_key_preserves_existing_lines_and_permissions(tmp_path):
    module = _load_device_auth_module()
    env_path = tmp_path / DOTENV_NAME
    env_path.write_text("XAI_API_KEY=xai_dummy\nSCRAPECREATORS_API_KEY=old\n", encoding="utf-8")
    env_path.chmod(0o644)

    module._upsert_env_key(env_path, "SCRAPECREATORS_API_KEY", "new_dummy")

    assert env_path.read_text(encoding="utf-8") == "XAI_API_KEY=xai_dummy\nSCRAPECREATORS_API_KEY=new_dummy\n"
    assert stat.S_IMODE(env_path.stat().st_mode) == 0o600
