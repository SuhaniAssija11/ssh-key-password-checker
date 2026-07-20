#!/usr/bin/env python3
"""Check SSH private keys for weak passphrases."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DICT_DIR = PROJECT_ROOT / "dictionaries"
COMMON_WORDLIST = DICT_DIR / "common.txt"
BRUTE_WORDLIST = DICT_DIR / "brute-1-4.txt"
COMBINED_WORDLIST = DICT_DIR / "combined.txt"


def is_private_key(path: Path) -> bool:
    try:
        return "PRIVATE KEY" in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def is_encrypted_key(path: Path) -> bool:
    sys.path.insert(0, str(SCRIPTS_DIR))
    from is_encrypted_key import is_encrypted_key as check_encrypted

    return check_encrypted(str(path))


def ensure_wordlists(max_length: int) -> Path:
    brute = DICT_DIR / f"brute-1-{max_length}.txt"
    combined = DICT_DIR / f"combined-1-{max_length}.txt"

    if not brute.exists():
        subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "generate-brute-wordlist.py"),
                "--max-length",
                str(max_length),
                "-o",
                str(brute),
            ],
            check=True,
        )

    if (
        not combined.exists()
        or brute.stat().st_mtime > combined.stat().st_mtime
        or COMMON_WORDLIST.stat().st_mtime > combined.stat().st_mtime
    ):
        combined.write_text(
            COMMON_WORDLIST.read_text(encoding="utf-8")
            + brute.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    return combined


def iter_passwords(wordlist: Path):
    with wordlist.open(encoding="utf-8") as handle:
        for line in handle:
            password = line.rstrip("\n")
            if password:
                yield password


def try_password(key: str, password: str) -> str | None:
    result = subprocess.run(
        ["ssh-keygen", "-y", "-f", key, "-P", password],
        capture_output=True,
        text=True,
    )
    return password if result.returncode == 0 else None


def crack_with_wordlist(
    key: Path,
    wordlist: Path,
    workers: int,
    timeout: float,
) -> str | None:
    deadline = time.monotonic() + timeout
    pending = set()
    passwords = iter_passwords(wordlist)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        while True:
            while len(pending) < workers * 4:
                if time.monotonic() >= deadline:
                    break
                try:
                    password = next(passwords)
                except StopIteration:
                    break
                pending.add(executor.submit(try_password, str(key), password))

            if not pending:
                break

            remaining = max(0.0, deadline - time.monotonic())
            if remaining == 0.0:
                break

            done, pending = wait(pending, timeout=remaining, return_when=FIRST_COMPLETED)
            for future in done:
                match = future.result()
                if match is not None:
                    for other in pending:
                        other.cancel()
                    return match

    return None


def find_private_keys(directory: Path) -> list[Path]:
    keys: list[Path] = []
    patterns = ("id_*", "*.pem", "*_key")
    for pattern in patterns:
        for path in directory.glob(pattern):
            if path.is_file() and is_private_key(path):
                keys.append(path)
        for path in directory.glob(f"*/{pattern}"):
            if path.is_file() and is_private_key(path):
                keys.append(path)
    return sorted(set(keys))


def check_key(
    key: Path,
    wordlist: Path,
    workers: int,
    timeout: float,
    quiet: bool,
) -> int:
    if not is_private_key(key):
        print(f"WARNING: Skipping {key}: not an SSH/OpenSSH private key", file=sys.stderr)
        return 0

    if not is_encrypted_key(key):
        print(f"UNPROTECTED\t{key}\t(no passphrase)")
        return 1

    match = crack_with_wordlist(key, wordlist, workers, timeout)
    if match is not None:
        print(f"WEAK\t{key}\t(passphrase cracked: {match})")
        return 1

    if not quiet:
        print(f"OK {key}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quickly check SSH private keys for weak passphrases."
    )
    parser.add_argument("keys", nargs="*", help="Private key files to check")
    parser.add_argument("--dir", type=Path, help="Directory to scan for private keys")
    parser.add_argument(
        "--max-length",
        type=int,
        default=4,
        help="Maximum generated brute-force password length (default: 4)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Per-key time limit in seconds (default: 60)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(2, min(8, os.cpu_count() or 4)),
        help="Parallel workers for passphrase checks",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print keys with problems",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    keys = [Path(key).expanduser() for key in args.keys]

    if args.dir:
        keys.extend(find_private_keys(args.dir.expanduser()))

    if not keys:
        print("ERROR: No keys provided.", file=sys.stderr)
        return 2

    if shutil.which("ssh-keygen") is None:
        print("ERROR: ssh-keygen is required.", file=sys.stderr)
        return 2

    wordlist = ensure_wordlists(args.max_length)
    status = 0
    for key in keys:
        if check_key(key, wordlist, args.workers, args.timeout, args.quiet) != 0:
            status = 1

    return status


if __name__ == "__main__":
    raise SystemExit(main())
