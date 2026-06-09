---
phase: 1
title: "Device Auth Secret Output"
status: completed
priority: P1
effort: "3-4h"
dependencies: []
---

# Phase 1: Device Auth Secret Output

## Overview

Remove secret disclosure from the ScrapeCreators device-auth helper. The helper may confirm success and persist configuration, but must never print access tokens, API keys, or copy-paste shell commands containing secrets.

## Context Links

- Source finding: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/test_device_auth.py:104`
- Repo rule: `/Users/hvnguyen/Projects/last30days-skill/AGENTS.md:42`

## Requirements

- Functional: device flow still obtains profile and configures `SCRAPECREATORS_API_KEY`.
- Non-functional: stdout/stderr must not contain full or partial secret values.
- Compatibility: keep direct helper invocation usable for dev/support.

## Related Code Files

- Modify: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/test_device_auth.py`
- Create: `/Users/hvnguyen/Projects/last30days-skill/tests/test_device_auth_security.py`

## Tests Before

1. Add tests that simulate `_post` and `_get` returning dummy token/key values.
2. Assert captured output does not contain:
   - full access token
   - token prefix
   - full ScrapeCreators API key
   - `echo 'SCRAPECREATORS_API_KEY=...`
3. Assert configured env file is written with `0600` permissions when a key is returned.
4. Run targeted test and confirm red: `uv run pytest tests/test_device_auth_security.py`

## Implementation Steps

1. Update docstring: replace “prints your API key” with “configures your API key”.
2. Add small local helpers:
   - `_config_path()` returns `~/.config/last30days/.env` unless an override is injected for tests.
   - `_upsert_env_key(path, key, value)` writes/updates the env file and enforces `0o600`.
   - `_safe_profile_summary(profile)` returns non-secret metadata only.
3. Replace `Authorized! Access token: ...` with a generic success line.
4. On profile-fetch failure, print only the error and “token withheld”.
5. On success, write `SCRAPECREATORS_API_KEY` to the config file and print path + confirmation.
6. Do not write config until the profile response contains a non-empty `api_key`.
7. Never print raw profile JSON. If `api_key` is missing, print a non-secret summary of available non-sensitive fields only.

## Refactor

- Keep helpers in the script; no new shared secret module unless a second production call site needs it.
- Prefer explicit path injection for tests over environment mutation.
<!-- Updated: Validation Session 1 - config writes only after profile api_key exists; no raw profile JSON on any branch -->

## Tests After

1. Re-run targeted device-auth tests.
2. Run broader auth/config tests: `uv run pytest tests/test_device_auth_security.py tests/test_env_keychain.py tests/test_env_v3.py`

## Success Criteria

- [x] No live token/key appears in any device-auth output path.
- [x] No config write happens when profile response lacks `api_key`.
- [x] Config write preserves existing `.env` lines and creates missing parent dirs.
- [x] `.env` mode is `0600` on create and after update.
- [x] Targeted tests pass.

## Risk Assessment

- Risk: test flow accidentally exercises network. Mitigation: monkeypatch `_post`, `_get`, `webbrowser.open`, and `time.sleep`.
- Risk: overwriting user config. Mitigation: line-preserving upsert and focused tests.
