"""Command line interface."""

from __future__ import annotations

import argparse
import sys

from .formatters import to_json, to_markdown, to_text
from .parser import parse_logs
from .sources import load_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gha-fail-digest",
        description="Parse GitHub Actions logs into a compact failure summary.",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Log file, directory of .log/.txt files, GitHub logs ZIP, run URL, or '-' for stdin.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text", "markdown"],
        default="json",
        help="Output format. Defaults to json.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON when --format json is selected.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        digest = parse_logs(load_sources(args.inputs))
    except Exception as exc:  # noqa: BLE001 - CLI should convert failures into user-readable errors.
        print(f"gha-fail-digest: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(to_json(digest, pretty=not args.compact))
    elif args.format == "text":
        print(to_text(digest))
    else:
        print(to_markdown(digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
