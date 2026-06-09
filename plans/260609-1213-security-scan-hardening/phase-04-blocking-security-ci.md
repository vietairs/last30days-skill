---
phase: 4
title: "Blocking Security CI"
status: completed
priority: P1
effort: "3-4h"
dependencies: [1, 2, 3]
---

# Phase 4: Blocking Security CI

## Overview

Move CI security scans from advisory to blocking after confirming a clean baseline for dependencies and verified secrets.

## Context Links

- Workflow: `/Users/hvnguyen/Projects/last30days-skill/.github/workflows/security.yml:40`
- Workflow tests: `/Users/hvnguyen/Projects/last30days-skill/tests/test_security_workflow.py:19`
- Repo rule: `/Users/hvnguyen/Projects/last30days-skill/AGENTS.md:46`

## Requirements

- Functional: pull requests, main pushes, and manual dispatch still run dependency and secret scans.
- Security: `pip-audit` and TruffleHog failures block CI after baseline is clean.
- Process: do not flip blocking until baseline evidence is captured in implementation notes/PR.

## Related Code Files

- Modify: `/Users/hvnguyen/Projects/last30days-skill/.github/workflows/security.yml`
- Modify: `/Users/hvnguyen/Projects/last30days-skill/tests/test_security_workflow.py`

## Tests Before

1. Update workflow tests to expect blocking policy:
   - no `continue-on-error: true` on `pip-audit`
   - no `continue-on-error: true` on TruffleHog
   - comments explain baseline is now clean, not “advisory-first”
2. Run targeted test and confirm red: `uv run pytest tests/test_security_workflow.py`

## Baseline Gate

Before workflow edit, run:

```bash
uv export --locked --all-groups --no-hashes --format requirements-txt --output-file /tmp/last30days-requirements.txt
uvx --python 3.12 pip-audit -r /tmp/last30days-requirements.txt --progress-spinner=off
trufflehog filesystem --only-verified .
```

If local TruffleHog is unavailable or network-restricted, do not silently skip. Use the GitHub action run as baseline evidence before merging the blocking flip.

## Implementation Steps

1. Capture baseline result in PR notes or implementation summary.
2. Remove `continue-on-error: true` from both security steps, or set explicit `false` only if YAML style prefers it.
3. Replace advisory comments with blocking-policy comments.
4. Keep `--only-verified` to avoid noisy unverified secret findings.

## Refactor

- Do not change workflow triggers, permissions, or scanner versions in this phase.
- Do not weaken `--only-verified`.

## Tests After

1. `uv run pytest tests/test_security_workflow.py`
2. `uv run pytest`

## Success Criteria

- [x] Tests assert blocking behavior.
- [x] Workflow blocks on dependency audit and verified secret findings.
- [x] Baseline evidence exists before finalizing.

## Risk Assessment

- Risk: external scanner outage blocks merges. Mitigation: keep scanner versions pinned and document temporary override process in PR if needed.
- Risk: historical secret scan noise. Mitigation: retain `--only-verified`.
