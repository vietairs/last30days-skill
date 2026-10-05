#!/usr/bin/env bash
# CI job "tests": install Python 3.12 via uv and run the pytest suite.
# Runs from the repo root; shared by .github/workflows/validate.yml and scripts/local-ci.mjs.
set -euo pipefail

uv python install 3.12
uv run pytest
