# wdpassport-utils

Source: originally from https://github.com/KenMacD/wdpassport-utils (with contributions by funkypopcorn, Dan Lukes, and later maintainers).

Purpose: unlock WD Security locked external drives on Linux and mount them after successful authentication.

What I changed in this update:
- Improved UI: cleaner layout, read-only log, `Show password`, `Clear log`.
- Improved security: no shell password execution, no password in process args, secure temp payload cleanup.
- Improved command safety: safer subprocess usage and required-tool checks.
- Added Linux app packaging + launcher files: `build-linux.sh`, `wd-security-launcher.sh`, `install-desktop-entry.sh`.

Double-click on Linux:
1. Build app: `./build-linux.sh`
2. Install desktop launcher: `./install-desktop-entry.sh`
3. Open app from launcher: **WD Security Unlocker**

Notes:
- This tool needs root privileges to unlock/mount drives.
- If `dist/wd-security` is not built yet, the launcher falls back to `wd-security.py`.
