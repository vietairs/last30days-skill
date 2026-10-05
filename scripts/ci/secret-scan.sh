#!/usr/bin/env bash
# CI job "Secret scan": TruffleHog OSS, verified secrets only (blocking).
# Runs the pinned release binary directly instead of the trufflesecurity/trufflehog
# action, because the action needs Docker, which the self-hosted Linux runner and the
# local container do not have. Runs from the repo root; shared by
# .github/workflows/security.yml and scripts/local-ci.mjs.
# Contributor policy: never commit real secrets in fixtures, tests, docs, or
# examples; use obvious dummy values and env-based auth patterns instead.
set -euo pipefail

version="3.95.2"
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) platform="linux_amd64" ;;
  Linux-aarch64 | Linux-arm64) platform="linux_arm64" ;;
  Darwin-arm64) platform="darwin_arm64" ;;
  Darwin-x86_64) platform="darwin_amd64" ;;
  *) echo "secret-scan: unsupported platform $(uname -s)-$(uname -m)" >&2; exit 1 ;;
esac

work_dir="$(mktemp -d "${RUNNER_TEMP:-${TMPDIR:-/tmp}}/trufflehog.XXXXXX")"
trap 'rm -rf "$work_dir"' EXIT

curl -fsSL --retry 3 \
  "https://github.com/trufflesecurity/trufflehog/releases/download/v${version}/trufflehog_${version}_${platform}.tar.gz" \
  | tar -xz -C "$work_dir" trufflehog

# Job-scoped git config (no writes to the global gitconfig): the tree may be owned by another uid.
export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0=safe.directory
export GIT_CONFIG_VALUE_0="$PWD"

# Pull requests: scan the range since the base branch. Everything else (push,
# dispatch, local run): scan the full history of the checkout.
since=()
if [ "${GITHUB_EVENT_NAME:-}" = "pull_request" ] && [ -n "${GITHUB_BASE_REF:-}" ] \
  && git rev-parse --verify --quiet "origin/${GITHUB_BASE_REF}" >/dev/null; then
  since=(--since-commit "origin/${GITHUB_BASE_REF}")
fi

"$work_dir/trufflehog" git "file://$PWD" ${since[@]+"${since[@]}"} --only-verified --fail --no-update
