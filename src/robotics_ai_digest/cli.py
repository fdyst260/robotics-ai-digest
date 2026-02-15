import argparse
from collections import OrderedDict

from . import __version__
from .feeds.rss_reader import fetch_rss
from .storage.db import init_db
from .storage.repository import get_recent_articles, upsert_articles


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="robotics_ai_digest",
        description="CLI for the robotics-ai-digest portfolio project.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("version", help="Show package version")
    fetch_parser = subparsers.add_parser("fetch", help="Fetch RSS items from URLs")
    fetch_parser.add_argument("--rss", nargs="+", required=True, help="RSS feed URLs")
    ingest_parser = subparsers.add_parser("ingest", help="Fetch RSS and persist new items")
    ingest_parser.add_argument("--db", required=True, help="Path to SQLite database")
    ingest_parser.add_argument("--rss", nargs="+", required=True, help="RSS feed URLs")
    list_parser = subparsers.add_parser("list", help="List recent stored articles")
    list_parser.add_argument("--db", required=True, help="Path to SQLite database")
    list_parser.add_argument("--limit", type=int, default=10, help="Maximum number of articles to show")
    list_parser.add_argument("--source", default=None, help="Filter by source name")

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
    if args.command == "ingest":
        session_factory = init_db(args.db)
        items = fetch_rss(args.rss)
        with session_factory() as session:
            nb_new, nb_duplicates = upsert_articles(session, items)
        print(f"Total retrieved: {len(items)}")
        print(f"New: {nb_new}")
        print(f"Duplicates: {nb_duplicates}")
        return 0
    if args.command == "list":
        session_factory = init_db(args.db)
        with session_factory() as session:
            articles = get_recent_articles(session, limit=args.limit, source=args.source)

        print(f"Showing {len(articles)} most recent articles")
        if not articles:
            print("No articles found.")
            return 0

        grouped: OrderedDict[tuple[str, str], list[str]] = OrderedDict()
        for article in articles:
            dt = article.published or article.created_at
            date_label = dt.date().isoformat()
            key = (date_label, article.source)
            grouped.setdefault(key, []).append(article.title)

        for (date_label, source_name), titles in grouped.items():
            print(f"[{date_label}] {source_name}")
            for title in titles:
                print(f"  - {title}")
        return 0

    parser.print_help()
    return 0
