#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="$ROOT_DIR/dist/wd-security"
SRC_PATH="$ROOT_DIR/wd-security.py"

CMD=()
if [[ -x "$BIN_PATH" ]]; then
  CMD=("$BIN_PATH")
elif command -v python3 >/dev/null 2>&1; then
  if ! python3 -c 'import PyQt5' >/dev/null 2>&1; then
    echo "python3 found, but PyQt5 is missing. Install PyQt5 or build the binary with ./build-linux.sh."
    exit 1
  fi
  CMD=(python3 "$SRC_PATH")
else
  echo "No runnable app found."
  echo "Build first with ./build-linux.sh or install python3 + PyQt5."
  exit 1
fi

if command -v pkexec >/dev/null 2>&1; then
  exec pkexec "${CMD[@]}"
fi

if command -v sudo >/dev/null 2>&1; then
  exec sudo "${CMD[@]}"
fi

echo "Neither pkexec nor sudo is available. Cannot run with required root permissions."
exit 1
