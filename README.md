# wdpassport-utils

Source: originally from https://github.com/KenMacD/wdpassport-utils (with contributions by funkypopcorn, Dan Lukes, and later maintainers).

Purpose: unlock WD Security locked external drives on Linux and mount them after successful authentication.

What I changed in this update:
- Improved the PyQt UI: cleaner layout/colors, read-only log area, `Show password`, and `Clear log`.
- Hardened security: removed shell-based password execution, avoided password in process args, used secure temporary payload file with cleanup.
- Improved command safety: switched to safer subprocess calls and stronger required-tool checks.
