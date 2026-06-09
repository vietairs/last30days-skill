---
phase: 3
title: "HTML Link Scheme Safety"
status: completed
priority: P1
effort: "2-3h"
dependencies: []
---

# Phase 3: HTML Link Scheme Safety

## Overview

Prevent saved HTML briefs from turning unsafe markdown link schemes into clickable links. Keep allowed links working for normal citations.

## Context Links

- Finding source: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/lib/html_render.py:599`
- Existing tests: `/Users/hvnguyen/Projects/last30days-skill/tests/test_html_render.py:191`

## Requirements

- Functional: `http`, `https`, and `mailto` markdown links may render as anchors.
- Security: `javascript:`, `data:`, `vbscript:`, empty, relative, entity-obfuscated, or mixed-case unsafe schemes must not be clickable.
- Compatibility: escaped text must remain valid HTML and parseable.

## Related Code Files

- Modify: `/Users/hvnguyen/Projects/last30days-skill/skills/last30days/scripts/lib/html_render.py`
- Modify: `/Users/hvnguyen/Projects/last30days-skill/tests/test_html_render.py`

## Tests Before

1. Add tests for:
   - `[x](javascript:alert(1))`
   - `[x](JaVaScRiPt:alert(1))`
   - `[x](&#106;avascript:alert(1))`
   - `[x](&amp;#106;avascript:alert(1))`
   - `[x](data:text/html,...)`
   - valid `https://`, `http://`, and `mailto:`
2. Assert unsafe cases have no `<a href=` and retain escaped visible text.
3. Run targeted test and confirm red: `uv run pytest tests/test_html_render.py -k link`

## Implementation Steps

1. Add a tiny `_safe_link_href(raw_href: str) -> str | None` helper.
2. Decode HTML entities before URL parsing. Repeat decoding until stable with a small cap so `&amp;#106;avascript:` cannot bypass the scheme check.
3. Use `urllib.parse.urlsplit` and allow only `http`, `https`, `mailto`.
4. Escape href value with `html.escape(..., quote=True)` after validation.
5. Replace regex substitution callback so unsafe links render as escaped label + href text, not an anchor.

## Refactor

- Keep markdown parser lightweight. Do not introduce a markdown dependency for one inline construct.
- Keep code-token protection order unchanged.
<!-- Updated: Validation Session 1 - entity-obfuscated unsafe hrefs need repeated decode coverage -->

## Tests After

1. `uv run pytest tests/test_html_render.py`
2. Verify rendered HTML still contains no `<script` in existing self-containedness test.

## Success Criteria

- [x] Unsafe schemes never produce clickable anchors.
- [x] Valid citation links still render.
- [x] Existing HTML snapshots remain parseable.

## Risk Assessment

- Risk: breaking unusual citation URLs. Mitigation: only block non-web/mail schemes; source URLs are expected to be absolute web URLs.
