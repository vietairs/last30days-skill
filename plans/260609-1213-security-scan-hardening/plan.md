---
title: "Security Scan Hardening"
description: "Close the June 9 security-scan findings with tests-first fixes for secret output, browser-cookie consent, HTML link schemes, and CI enforcement."
status: completed
priority: P1
effort: "1-2d"
branch: "main"
tags: [security, bugfix, infra, docs]
blockedBy: []
blocks: []
created: "2026-06-09T02:14:19.838Z"
createdBy: "ck:plan"
source: skill
---

# Security Scan Hardening

## Overview

Harden `last30days-skill` at commit `1221584` against four security-scan findings: secret-bearing helper output, implicit browser-cookie reads, unsafe HTML markdown links, and advisory-only security CI. Use targeted fixes. No broad refactor. Keep slash-command UX and docs in sync with engine behavior.

Source report and brainstorm: [security-hardening-brainstorm-report.md](./reports/security-hardening-brainstorm-report.md)

## Constraints

- Follow `AGENTS.md`: `SKILL.md` is runtime source of truth; update `CONFIGURATION.md` when config behavior changes.
- `.agents/rules/development-rules.md` is referenced but absent in this checkout. Use injected AGENTS rules and README constraints.
- Do not restore or modify repo-local skills.
- Keep changes scoped to the four scan findings.
- `skills/last30days/nux-wizard.md` is referenced by `SKILL.md` but absent. Treat as setup-flow constraint; do not expand scope into wizard restoration unless required by tests.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Device Auth Secret Output](./phase-01-device-auth-secret-output.md) | Completed |
| 2 | [Browser Cookie Consent](./phase-02-browser-cookie-consent.md) | Completed |
| 3 | [HTML Link Scheme Safety](./phase-03-html-link-scheme-safety.md) | Completed |
| 4 | [Blocking Security CI](./phase-04-blocking-security-ci.md) | Completed |
| 5 | [Documentation and Verification](./phase-05-documentation-and-verification.md) | Completed |

## Dependencies

- No existing project plans found under `plans/`.
- Phase 4 depends on clean baseline verification after Phases 1-3.

## Success Criteria

- `uv run pytest` passes.
- Targeted tests cover all four findings.
- No helper path prints full or partial live access tokens/API keys.
- Unset `FROM_BROWSER` reads no browser cookies.
- Exported HTML never emits clickable `javascript:` or other unsafe schemes.
- CI security checks are blocking only after baseline verification is captured during implementation.
- User-facing docs match actual auth and setup behavior.

## Unresolved Questions

None.

## Validation Log

### Session 1 — 2026-06-09
**Trigger:** `/ck:plan validate` before implementation  
**Questions asked:** 0

#### Verification Results

- **Tier:** Full (5 phases)
- **Claims checked:** 31
- **Verified:** 29 | **Failed:** 0 | **Unverified:** 2
- **Unverified:** local `trufflehog` binary is not installed on this machine; `skills/last30days/nux-wizard.md` is referenced by `SKILL.md` but absent.

#### Source-Verified Findings

- Device auth leak sites verified in `skills/last30days/scripts/test_device_auth.py`: token prefix, full failure token, profile JSON, API key, and `echo` command.
- Browser-cookie default path verified in `skills/last30days/scripts/lib/env.py`: unset `FROM_BROWSER` tries Firefox/Safari.
- Setup path verified in `skills/last30days/scripts/last30days.py` and `skills/last30days/scripts/lib/setup_wizard.py`: `setup` currently runs cookie scan and writes `FROM_BROWSER` without separate consent.
- HTML link conversion verified in `skills/last30days/scripts/lib/html_render.py`: markdown link href is inserted without scheme validation.
- CI advisory policy verified in `.github/workflows/security.yml` and `tests/test_security_workflow.py`.

#### Confirmed Decisions

- No new user decisions required. Existing approved direction covers all validation findings.
- Tighten Phase 1: no config write until profile returns `api_key`; never print raw profile JSON, including missing-key responses.
- Tighten Phase 2: consent requirement applies to both `env.get_config()` and `setup_wizard.run_auto_setup()`.
- Tighten Phase 3: entity-obfuscated hrefs require repeated HTML-entity decoding before scheme validation.

#### Action Items

- [x] Propagate the three tightened constraints into phase files.
- [x] Run whole-plan consistency sweep after propagation.

### Whole-Plan Consistency Sweep

- Files reread: `plan.md`, `phase-01-device-auth-secret-output.md`, `phase-02-browser-cookie-consent.md`, `phase-03-html-link-scheme-safety.md`, `phase-04-blocking-security-ci.md`, `phase-05-documentation-and-verification.md`
- Decision deltas checked: 3
- Reconciled stale references: 3
- Unresolved contradictions: 0

### Session 2 — 2026-06-09
**Trigger:** `/ck:cook plans/260609-1213-security-scan-hardening/plan.md` implementation  
**Questions asked:** 1 privacy-hook approval for patch text containing config filename literals.

#### Implementation Results

- Hardened standalone device-auth helper and runtime setup auth JSON paths so ScrapeCreators keys are persisted locally and not printed.
- Changed unset `FROM_BROWSER` to no browser-cookie reads; explicit `auto`, `firefox`, `safari`, and `chrome` still work.
- Gated setup cookie scans and browser-mode persistence behind explicit `BROWSER_CONSENT=true` plus `FROM_BROWSER`.
- Added HTML href scheme validation with repeated entity decoding; anchors now allow only `http`, `https`, and `mailto`.
- Converted security workflow to blocking dependency and verified-secret scans; also updated `uv export` format to `requirements-txt`, matching the local toolchain.
- Updated README, runtime `SKILL.md`, `CONFIGURATION.md`, and Hermes setup docs for opt-in browser-cookie behavior.

#### Verification Results

- Targeted setup-auth tests after review fixes: `44 passed`.
- Targeted security tests: `20 passed, 85 deselected, 8 subtests passed`.
- Full suite: `1628 passed, 4 skipped, 10 subtests passed`.
- Diff hygiene: `git diff --check` passed.
- Stale wording search for old browser-cookie claims returned no matches.
- Secret-output search returned one intentional negative assertion only.
- Dependency baseline: `uvx --python 3.12 pip-audit -r /tmp/last30days-requirements.txt --progress-spinner=off` reported no known vulnerabilities.
- Verified-secret baseline: local `trufflehog` unavailable; latest GitHub `Security` run `27161036423` succeeded on 2026-06-08 with both `Secret scan` and `Dependency audit` jobs green.

#### Review Results

- Tester subagent found no functional regressions in validated paths.
- Code reviewer found a critical JSON stdout leak in setup auth paths; fixed with runtime persistence and CLI stdout regression tests.
- Re-review found blank-key config write and raw PAT no-key response logging risks; fixed with defensive blank-key rejection and sanitized logging tests.

#### Unresolved Questions

None.
