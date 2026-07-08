#!/usr/bin/env python3
"""Generate passwords up to max_length from a character set."""

import argparse
import itertools
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a wordlist of all strings up to a max length."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="-",
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=4,
        help="Maximum password length to generate (default: 4)",
    )
    parser.add_argument(
        "--charset",
        default="abcdefghijklmnopqrstuvwxyz0123456789",
        help="Characters to use when generating passwords",
    )
    args = parser.parse_args()

    if args.max_length < 1:
        parser.error("--max-length must be at least 1")

    out = open(args.output, "w", encoding="utf-8") if args.output != "-" else sys.stdout
    try:
        for length in range(1, args.max_length + 1):
            for combo in itertools.product(args.charset, repeat=length):
                out.write("".join(combo) + "\n")
    finally:
        if out is not sys.stdout:
            out.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
