---
phase: 2
title: "Browser Cookie Consent"
status: completed
priority: P1
effort: "4-5h"
dependencies: []
---

# Phase 2: Browser Cookie Consent

## Overview

Make browser-cookie extraction explicit opt-in. Unset `FROM_BROWSER` must behave like `off`; only `FROM_BROWSER=firefox|safari|chrome|auto` may read local browser cookies.

## Context Links

- Finding source: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/lib/env.py:403`
- Runtime spec: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/SKILL.md:248`
- Config docs: `/Users/hvnguyen/Projects/last30days-skill/CONFIGURATION.md:58`

## Requirements

- Functional: explicit `FROM_BROWSER` values still work.
- Non-functional: no silent cookie reads on default path.
- Documentation: `SKILL.md`, `CONFIGURATION.md`, and Hermes setup text must describe opt-in behavior.

## Related Code Files

- Modify: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/lib/env.py`
- Modify: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/lib/setup_wizard.py`
- Modify: `/Users/hvnguyen/Projects/last30days-skill/tests/test_env_cookies.py`
- Modify: `/Users/hvnguyen/Projects/last30days-skill/tests/test_setup_wizard.py`
- Modify: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/SKILL.md`
- Modify: `/Users/hvnguyen/Projects/last30days-skill/CONFIGURATION.md`
- Modify: `/Users/hvnguyen/Projects/last30days-skill/HERMES_SETUP.md`

## Tests Before

1. Change `test_no_from_browser_defaults_to_silent` to expect no extraction calls.
2. Add/adjust `get_config()` integration test: no `FROM_BROWSER` must not inject `AUTH_TOKEN`/`CT0`.
3. Add setup-config test: default `write_setup_config()` should not write `FROM_BROWSER=auto` unless caller passes explicit consent.
4. Add setup-command/auto-setup test: `run_auto_setup({})` must not call `cookie_extract.extract_cookies_with_source` unless explicit cookie consent is present in config or arguments.
5. Run targeted tests and confirm red: `uv run pytest tests/test_env_cookies.py tests/test_setup_wizard.py`

## Implementation Steps

1. In `extract_browser_credentials`, return `{}` when `FROM_BROWSER` is unset or `off`.
2. Preserve explicit values:
   - `firefox`, `safari`, `chrome` try only that browser.
   - `auto` tries the existing ordered browser list.
3. Update docstring and comments to remove “default silent browsers”.
4. Update setup config default to consent-safe:
   - default `from_browser="off"` or no browser line unless consented.
   - explicit consent paths may still write `BROWSER_CONSENT=true` + `FROM_BROWSER=auto`.
5. Update `run_auto_setup` so cookie extraction is skipped unless explicit browser-cookie consent exists. It may still check `yt-dlp` without cookie consent.
6. Update `last30days.py setup` so it does not infer/write `FROM_BROWSER` from a scan that was not explicitly consented.
7. Update `SKILL.md` source detection and just-in-time unlock wording.
8. Update `CONFIGURATION.md` and `HERMES_SETUP.md`: browser cookies are opt-in, not default.

## Refactor

- Do not remove `cookie_extract.py`; it remains valid behind explicit opt-in.
- Avoid adding new consent state unless existing `FROM_BROWSER` is insufficient. `BROWSER_CONSENT=true` can remain doc-level/flow metadata.
<!-- Updated: Validation Session 1 - setup auto-scan is also in scope for explicit browser-cookie consent -->

## Tests After

1. `uv run pytest tests/test_env_cookies.py tests/test_setup_wizard.py tests/test_cookie_extract.py`
2. `uv run pytest tests/test_skill_meta.py tests/test_version_consistency.py` if `SKILL.md` changes affect metadata checks.

## Success Criteria

- [x] Unset `FROM_BROWSER` performs zero browser extraction calls.
- [x] `FROM_BROWSER=auto` still extracts test cookies.
- [x] First-run/setup config no longer silently opts users into browser reads.
- [x] `setup` command does not scan cookies without explicit consent.
- [x] Docs and runtime spec agree.

## Risk Assessment

- Risk: fewer first-run X results. Mitigation: keep just-in-time X unlock prompt.
- Risk: stale tests encode old default. Mitigation: update tests before code.
