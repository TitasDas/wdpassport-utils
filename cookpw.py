#!/usr/bin/env python

from __future__ import print_function
from hashlib import sha256
import sys


def _to_bytes(value):
    try:
        return value.encode('utf-8')
    except AttributeError:
        return value


def main(password):
    """Print the data block required to unlock the drive."""
    password = 'WDC.' + password
    password = password.encode('utf-16')[2:]  # remove UTF-16 BOM

    for _ in range(1000):
        password = sha256(password).digest()

    # Protocol header, then hashed payload.
    header = '45'      # Signature
    header += '0000000000'  # Reserved
    header += '0020'   # Password length

    try:
        header_bytes = header.decode('hex')  # Python 2
    except AttributeError:
        header_bytes = bytes.fromhex(header)  # Python 3

    data = header_bytes + password

    # Write as bytes in both Python 2 and 3.
    out = getattr(sys.stdout, 'buffer', sys.stdout)
    out.write(data)


def _read_password_from_stdin():
    data = sys.stdin.read()
    if data is None:
        return ''
    return data.rstrip('\r\n')


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--stdin':
        main(_read_password_from_stdin())
        sys.exit(0)

    if len(sys.argv) != 2:
        print('Usage: {0} <password> | {0} --stdin'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    main(sys.argv[1])
