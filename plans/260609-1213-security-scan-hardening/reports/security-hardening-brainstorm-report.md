---
type: report
title: "Security Scan Hardening Brainstorm"
status: approved
created: 2026-06-09
source: ck:brainstorm
---

# Security Scan Hardening Brainstorm

## Summary

Approved design: targeted tests-first hardening for all four June 9 security-scan findings in `mvanhorn/last30days-skill` at commit `1221584`.

Recommended approach: minimal targeted patch. No central security framework. No feature removal. Keep current slash-command UX, but make browser-cookie access explicit.

## Scout Findings

- Project: Python 3.12 Agent Skill package. Runtime source: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/SKILL.md`.
- Runtime deps: none in `/Users/hvnguyen/Projects/last30days-skill/pyproject.toml`.
- Test suite: pytest under `/Users/hvnguyen/Projects/last30days-skill/tests`.
- Finding 1 real: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/test_device_auth.py` prints token/key material.
- Finding 2 real: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/lib/env.py` reads Firefox/Safari cookies when `FROM_BROWSER` unset.
- Finding 3 real: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/lib/html_render.py` converts markdown links without scheme validation.
- Finding 4 real but policy-shaped: `/Users/hvnguyen/Projects/last30days-skill/.github/workflows/security.yml` and tests encode advisory CI.
- Constraint: `.agents/rules/development-rules.md` missing. Used README and injected AGENTS rules.

## Requirements

- Expected output: implementation plan and phase files for security fixes.
- Acceptance: all four findings have concrete test/code/doc changes; final plan is actionable.
- Scope: report findings only. No unrelated refactor. No repo-local skills.
- Non-negotiable: update `SKILL.md` and `CONFIGURATION.md` when behavior changes.
- Touchpoints: device auth helper, env cookie config, HTML renderer, security workflow, tests, docs.

## Evaluated Approaches

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| Minimal targeted patch | Low blast radius, fast, fits existing tests | Less reusable | Choose |
| Central security helper module | Reusable redaction/url policy | Overbuilt for three narrow sites | Reject |
| Remove risky features | Strong posture | Breaks useful setup/auth UX | Reject |

## Final Recommendation

Use tests-first targeted changes:

1. Device auth: never print access token/API key; persist key to `0600` config; output only confirmation.
2. Browser cookies: unset `FROM_BROWSER` means off; explicit `FROM_BROWSER=firefox|safari|chrome|auto` required.
3. HTML links: allow only `http`, `https`, `mailto`; unsafe markdown links render as escaped text.
4. CI: verify clean baseline, then make `pip-audit` and TruffleHog blocking.

## Risks

- Browser opt-in can reduce X coverage for users relying on silent cookie discovery. Mitigate with just-in-time X unlock prompt.
- CI blocking can fail on external scanner instability. Mitigate with pinned versions and baseline evidence.
- Device-auth config write can overwrite user settings. Mitigate with line-preserving upsert tests.

## Validation Criteria

- `uv run pytest`
- `git diff --check`
- Targeted secret-output search has no unsafe production hits.
- Baseline `pip-audit` and verified-secret scan clean before CI flip.

## Next Steps

- Execute `/ck:plan --tdd` plan in this directory.
- Implement phases in order.
- Re-run full test suite and security baseline before final summary.

## Unresolved Questions

None.
