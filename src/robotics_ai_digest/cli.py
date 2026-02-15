import argparse

from . import __version__
from .feeds.rss_reader import fetch_rss


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="robotics_ai_digest",
        description="CLI for the robotics-ai-digest portfolio project.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("version", help="Show package version")
    fetch_parser = subparsers.add_parser("fetch", help="Fetch RSS items from URLs")
    fetch_parser.add_argument("--rss", nargs="+", required=True, help="RSS feed URLs")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        print(__version__)
        return 0
    if args.command == "fetch":
        items = fetch_rss(args.rss)
        print(f"Total items: {len(items)}")
        for item in items[:5]:
            print(f"- {item.get('title')}")
        return 0

    parser.print_help()
    return 0
