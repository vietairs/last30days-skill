#!/usr/bin/env bash
# CI job "Secret scan": TruffleHog OSS, verified secrets only (blocking).
# Runs the pinned release binary directly instead of the trufflesecurity/trufflehog
# action, because the action needs Docker, which the self-hosted Linux runner and the
# local container do not have. Runs from the repo root; shared by
# .github/workflows/security.yml and .github/ci/local-ci.mjs.
# Contributor policy: never commit real secrets in fixtures, tests, docs, or
# examples; use obvious dummy values and env-based auth patterns instead.
#
# Scan range mirrors the trufflesecurity/trufflehog action:
#   pull_request     --since-commit PR_BASE_SHA --branch PR_HEAD_SHA
#   push             --branch PUSH_AFTER (+ --since-commit PUSH_BEFORE unless new branch)
#   dispatch / local no range: full history of the checkout
# --branch is required alongside --since-commit: without a head, trufflehog walks
# `git log --all` and stops at the first commit equal to the base, which can skip
# the PR commits entirely when the base branch has newer commits than the PR.
set -euo pipefail

version="3.95.2"
# sha256 of each release tarball, from trufflehog_${version}_checksums.txt.
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)
    platform="linux_amd64"
    sha256="fded1c139fe4d3872d9fde65e1428d82d5556d655439e82f492d87ae8d846779" ;;
  Linux-aarch64 | Linux-arm64)
    platform="linux_arm64"
    sha256="5588f09da2d52e840273b6a8c57751021709182dff42574f09dbaf81ebdf8366" ;;
  Darwin-arm64)
    platform="darwin_arm64"
    sha256="382c719794eda239e6d4944ea40efbdce65e8b6a36cd030948254068e666185c" ;;
  Darwin-x86_64)
    platform="darwin_amd64"
    sha256="e414f488fcf0c39f2b2ce283eaa15ab37cab4569e03a5763d19dc592ca4b0cdd" ;;
  *) echo "secret-scan: unsupported platform $(uname -s)-$(uname -m)" >&2; exit 1 ;;
esac

work_dir="$(mktemp -d "${RUNNER_TEMP:-${TMPDIR:-/tmp}}/trufflehog.XXXXXX")"
trap 'rm -rf "$work_dir"' EXIT

tarball="$work_dir/trufflehog.tar.gz"
curl -fsSL --retry 3 -o "$tarball" \
  "https://github.com/trufflesecurity/trufflehog/releases/download/v${version}/trufflehog_${version}_${platform}.tar.gz"

# Integrity check before anything from the tarball is extracted or run.
if command -v sha256sum >/dev/null 2>&1; then
  echo "${sha256}  ${tarball}" | sha256sum -c - >/dev/null
else
  echo "${sha256}  ${tarball}" | shasum -a 256 -c - >/dev/null
fi
tar -xz -C "$work_dir" -f "$tarball" trufflehog

args=(--only-verified --fail --no-update)
# Workflow annotations on the PR; plain output for local runs.
if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
  args+=(--github-actions)
fi

zeros="0000000000000000000000000000000000000000"
case "${GITHUB_EVENT_NAME:-}" in
  pull_request)
    if [ -n "${PR_BASE_SHA:-}" ] && [ "${PR_BASE_SHA:-}" = "${PR_HEAD_SHA:-}" ]; then
      # Same failure the trufflesecurity/trufflehog action raised: a range with
      # identical ends would scan nothing and pass.
      echo "secret-scan: BASE and HEAD commits are the same, so there is nothing to scan." >&2
      exit 1
    fi
    if [ -n "${PR_BASE_SHA:-}" ] && [ -n "${PR_HEAD_SHA:-}" ]; then
      args+=(--since-commit "$PR_BASE_SHA" --branch "$PR_HEAD_SHA")
    fi
    ;;
  push)
    if [ -n "${PUSH_AFTER:-}" ]; then
      if [ -n "${PUSH_BEFORE:-}" ] && [ "$PUSH_BEFORE" = "$PUSH_AFTER" ]; then
        echo "secret-scan: BASE and HEAD commits are the same, so there is nothing to scan." >&2
        exit 1
      fi
      args+=(--branch "$PUSH_AFTER")
      if [ -n "${PUSH_BEFORE:-}" ] && [ "$PUSH_BEFORE" != "$zeros" ]; then
        args+=(--since-commit "$PUSH_BEFORE")
      fi
    fi
    ;;
esac

"$work_dir/trufflehog" git "file://$PWD" "${args[@]}"
