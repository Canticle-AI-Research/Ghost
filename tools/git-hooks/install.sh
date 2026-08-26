#!/usr/bin/env bash
# Install Ghost's canonical pre-commit hook into .git/hooks/.
#
# Symlinks where supported so the hook tracks the repository copy; falls back to
# a plain copy on filesystems without symlink support.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SOURCE="${REPO_ROOT}/tools/git-hooks/pre-commit"
TARGET="${REPO_ROOT}/.git/hooks/pre-commit"

[ -f "${SOURCE}" ] || { echo "missing ${SOURCE}" >&2; exit 1; }
chmod +x "${SOURCE}"
mkdir -p "$(dirname "${TARGET}")"

if [ -e "${TARGET}" ] && [ ! -L "${TARGET}" ]; then
  cp "${TARGET}" "${TARGET}.replaced-$(date +%Y%m%d-%H%M%S)"
  echo "existing hook backed up alongside ${TARGET}"
fi

if ln -sf "${SOURCE}" "${TARGET}" 2>/dev/null; then
  echo "installed pre-commit hook (symlink) -> ${SOURCE}"
else
  cp "${SOURCE}" "${TARGET}"
  chmod +x "${TARGET}"
  echo "installed pre-commit hook (copy) -> ${TARGET}"
fi
