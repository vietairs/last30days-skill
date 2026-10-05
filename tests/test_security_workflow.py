from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"
# AGENTS.md is the canonical agent-guidance file; CLAUDE.md is a one-line
# pointer (`@AGENTS.md`) so anything Claude Code-shaped reads the same source.
AGENTS = ROOT / "AGENTS.md"


CI_SCRIPTS = ROOT / ".github" / "ci"


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _script_text(name: str) -> str:
    return (CI_SCRIPTS / name).read_text(encoding="utf-8")


def test_security_workflow_exists() -> None:
    assert WORKFLOW.is_file()


def test_security_workflow_runs_dependency_audit_as_blocking_gate() -> None:
    text = _workflow_text()
    script = _script_text("dependency-audit.sh")

    assert "dependency-audit:" in text
    assert ".github/ci/dependency-audit.sh" in text
    assert "pip-audit" in script
    assert "--format requirements-txt" in script
    dep_job = text.split("dependency-audit:", 1)[1].split("secret-scan:", 1)[0]
    assert "continue-on-error: true" not in dep_job
    assert "clean baseline run is confirmed" in dep_job


def test_security_workflow_runs_secret_scan_for_pull_requests_and_main_pushes() -> None:
    text = _workflow_text()
    script = _script_text("secret-scan.sh")

    assert "secret-scan:" in text
    assert ".github/ci/secret-scan.sh" in text
    assert "  pull_request:" in text
    assert "  push:" in text
    assert "trufflesecurity/trufflehog" in script
    assert "pull_request" in script
    assert "--only-verified" in script


def test_secret_scan_pull_request_range_passes_head_branch() -> None:
    text = _workflow_text()
    script = _script_text("secret-scan.sh")

    # trufflehog stops at the base commit when no head is set, which can skip PR
    # commits; the PR range must always pair --since-commit with --branch.
    assert '--since-commit "$PR_BASE_SHA" --branch "$PR_HEAD_SHA"' in script
    assert '--branch "$PUSH_AFTER"' in script
    assert '--since-commit "$PUSH_BEFORE"' in script
    assert "--github-actions" in script
    secret_job = text.split("secret-scan:", 1)[1]
    for name in ("PR_BASE_SHA", "PR_HEAD_SHA", "PUSH_BEFORE", "PUSH_AFTER"):
        assert f"{name}: ${{{{ github.event." in secret_job


def test_secret_scan_fails_when_range_ends_are_identical() -> None:
    script = _script_text("secret-scan.sh")

    # The replaced action failed on BASE == HEAD; a silent pass would hide a
    # re-run that scanned nothing.
    assert '"${PR_BASE_SHA:-}" = "${PR_HEAD_SHA:-}"' in script
    assert '"$PUSH_BEFORE" = "$PUSH_AFTER"' in script
    assert "nothing to scan" in script


def test_secret_scan_verifies_pinned_binary_checksum() -> None:
    script = _script_text("secret-scan.sh")

    assert "sha256sum -c" in script
    assert "shasum -a 256 -c" in script


def test_security_workflow_documents_blocking_policy() -> None:
    text = _workflow_text()
    script = _script_text("secret-scan.sh")

    assert "blocking policy" in text.lower()
    assert "verified secrets block merges" in text.lower()
    assert "fixtures" in script.lower()
    assert "env-based auth" in script.lower()
    secret_job = text.split("secret-scan:", 1)[1]
    assert "continue-on-error: true" not in secret_job


def test_agent_guidance_mentions_secret_hygiene() -> None:
    text = AGENTS.read_text(encoding="utf-8")

    assert "Security hygiene" in text
    assert "Never commit real API keys" in text
    assert "skills/last30days/scripts/lib/env.py" in text
    assert "fixtures" in text
