---
type: journal
title: "Security Scan Hardening Plan"
created: 2026-06-09
source: ck:journal
---

# Security Scan Hardening Plan

## Context

User approved a `ck:brainstorm` design for the June 9 `ck:security-scan` report against `last30days-skill`.

## What Happened

- Scouted repo at commit `1221584`; working tree clean.
- Confirmed all four scan findings map to live files.
- Found `.agents/rules/development-rules.md` and `skills/last30days/nux-wizard.md` are referenced but absent.
- Created project plan at `plans/260609-1213-security-scan-hardening/`.

## Decisions

- Use targeted tests-first fixes.
- Keep browser-cookie extraction feature, but make it explicit opt-in.
- Make security CI blocking only after clean baseline proof.

## Next

Implement plan phases when user asks.

## Implementation Follow-Up

Cooked the plan end-to-end on 2026-06-09.

## What Changed

- Device auth helper writes `SCRAPECREATORS_API_KEY` to config with `0600` perms and no token/key stdout.
- Runtime setup auth paths now also persist keys internally and return only non-secret JSON.
- Unset `FROM_BROWSER` performs zero browser-cookie reads; setup scans only with explicit `BROWSER_CONSENT=true` plus `FROM_BROWSER`.
- HTML brief markdown links only create anchors for `http`, `https`, and `mailto` after repeated entity decoding.
- Security workflow now blocks on dependency audit and verified-secret scan failures.
- README, `SKILL.md`, `CONFIGURATION.md`, and Hermes setup text describe opt-in browser-cookie auth.

## Review Notes

- Code review caught a missed leak in `setup --device-auth` / `setup --github` JSON stdout; fixed with persistence and stdout regression tests.
- Re-review caught blank `api_key` writes and raw PAT no-key response logging; fixed with defensive blank rejection and sanitized logging.
- Local TruffleHog unavailable; latest GitHub `Security` run `27161036423` had green Secret scan and Dependency audit jobs.

## Proof

- `uv run pytest`: `1628 passed, 4 skipped, 10 subtests passed`.
- `git diff --check`: pass.
- `pip-audit`: no known vulnerabilities.
- Stale browser-cookie wording search: no matches.
- Secret-output search: one intentional negative assertion only.

## Unresolved Questions

None.
