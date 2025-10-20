#!/usr/bin/env python3
import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Override analog channel to fixed percent")
    parser.add_argument("--channel", required=True, help="Channel id, e.g. daily_home")
    parser.add_argument("--percent", type=float, help="0..100 percent; omit to disable override", nargs="?")
    args = parser.parse_args()

    # TODO: integrate with analog module once implemented
    if args.percent is None:
        print(f"Override OFF for {args.channel}")
        return 0
    if args.percent < 0 or args.percent > 100:
        print("Percent must be within 0..100", file=sys.stderr)
        return 2
    print(f"Override {args.channel} → {args.percent:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())






