#!/usr/bin/env python3
"""Return whether an SSH private key file is passphrase-protected."""

import base64
import re
import sys


def is_encrypted_key(path: str) -> bool:
    with open(path, encoding="utf-8", errors="replace") as handle:
        content = handle.read()

    if "-----BEGIN OPENSSH PRIVATE KEY-----" in content:
        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip() and "PRIVATE KEY" not in line
        ]
        blob = base64.b64decode("".join(lines))
        if not blob.startswith(b"openssh-key-v1\x00"):
            return False

        offset = len(b"openssh-key-v1\x00")
        cipher_len = int.from_bytes(blob[offset : offset + 4], "big")
        offset += 4 + cipher_len
        kdf_len = int.from_bytes(blob[offset : offset + 4], "big")
        offset += 4
        kdf_name = blob[offset : offset + kdf_len]
        return kdf_name != b"none"

    if "ENCRYPTED" in content:
        return True

    return bool(re.search(r"^Proc-Type:\s*4,ENCRYPTED", content, re.MULTILINE))


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} KEYFILE", file=sys.stderr)
        return 2

    print("yes" if is_encrypted_key(sys.argv[1]) else "no")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
