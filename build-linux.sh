#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "pyinstaller is not installed."
  echo "Install it first (example): pip install pyinstaller"
  exit 1
fi

# This project is PyQt4/Python2-era. Use PYTHON_BIN to pin interpreter if needed.
: "${PYTHON_BIN:=python}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Configured PYTHON_BIN '$PYTHON_BIN' was not found."
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
echo "Run with root privileges using: ./wd-security-launcher.sh"
