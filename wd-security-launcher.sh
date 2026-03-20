#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="$ROOT_DIR/dist/wd-security"
SRC_PATH="$ROOT_DIR/wd-security.py"

CMD=()
if [[ -x "$BIN_PATH" ]]; then
  CMD=("$BIN_PATH")
elif command -v python2 >/dev/null 2>&1; then
  CMD=(python2 "$SRC_PATH")
elif command -v python >/dev/null 2>&1; then
  CMD=(python "$SRC_PATH")
else
  echo "No runnable app found."
  echo "Build first with ./build-linux.sh or install python2."
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
