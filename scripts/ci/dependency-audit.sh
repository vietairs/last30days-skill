#!/usr/bin/env bash
# CI job "Dependency audit": export the locked dependency set and run pip-audit on it.
# Runs from the repo root; shared by .github/workflows/security.yml and scripts/local-ci.mjs.
set -euo pipefail

out_dir="${RUNNER_TEMP:-${TMPDIR:-/tmp}}"
requirements="$out_dir/last30days-requirements.txt"

# On a persistent self-hosted runner keep uv's Python installs and caches job-scoped.
if [ -n "${RUNNER_TEMP:-}" ]; then
  export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$RUNNER_TEMP/uv-python}"
  export UV_CACHE_DIR="${UV_CACHE_DIR:-$RUNNER_TEMP/uv-cache}"
fi

uv python install 3.12

uv export \
  --locked \
  --all-groups \
  --no-hashes \
  --format requirements-txt \
  --output-file "$requirements"

# Blocking policy: the clean baseline run is confirmed, so dependency
# CVEs fail CI instead of landing as advisory-only log output.
uvx --python 3.12 pip-audit -r "$requirements" --progress-spinner=off
