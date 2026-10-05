#!/usr/bin/env bash
# CI job "tests": install Python 3.12 via uv and run the pytest suite.
# Runs from the repo root; shared by .github/workflows/validate.yml and .github/ci/local-ci.mjs.
set -euo pipefail

# On a persistent self-hosted runner keep uv's Python installs and caches job-scoped.
if [ -n "${RUNNER_TEMP:-}" ]; then
  export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$RUNNER_TEMP/uv-python}"
  export UV_CACHE_DIR="${UV_CACHE_DIR:-$RUNNER_TEMP/uv-cache}"
fi

uv python install 3.12
uv run pytest
