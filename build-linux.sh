#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "pyinstaller is not installed."
  echo "Install it first (example): pip install pyinstaller"
  exit 1
fi

# This project is Python2/PyQt4 based.
if command -v python2 >/dev/null 2>&1; then
  PYTHON_BIN="${PYTHON_BIN:-python2}"
else
  PYTHON_BIN="${PYTHON_BIN:-python}"
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "No suitable Python runtime found for build."
  echo "Install python2 (recommended for this project), or set PYTHON_BIN explicitly."
  exit 1
fi

rm -rf build dist

"$PYTHON_BIN" -m PyInstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name wd-security \
  wd-security.py

echo "Build complete: $ROOT_DIR/dist/wd-security"
