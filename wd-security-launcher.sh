#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="$ROOT_DIR/dist/wd-security"
SRC_PATH="$ROOT_DIR/wd-security.py"

if [[ -x "$BIN_PATH" ]]; then
  TARGET="$BIN_PATH"
else
  TARGET="$SRC_PATH"
fi

if command -v pkexec >/dev/null 2>&1; then
  exec pkexec "$TARGET"
fi

if command -v sudo >/dev/null 2>&1; then
  exec sudo "$TARGET"
fi

echo "Neither pkexec nor sudo is available. Cannot run with required root permissions."
exit 1
