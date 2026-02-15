import argparse
from collections import OrderedDict
from datetime import date
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from . import __version__
from .digest.renderer_md import render_digest
from .feeds.rss_reader import fetch_rss
from .storage.db import init_db
from .storage.repository import (
    get_articles_for_date,
    get_articles_missing_ai_summary,
    get_recent_articles,
    save_ai_summary,
    upsert_articles,
)
from .summarization.cost_estimator import (
    DEFAULT_EXPECTED_OUTPUT_TOKENS,
    count_tokens,
    estimate_api_cost,
)
from .summarization.mock_summarizer import MockSummarizer
from .summarization.openai_summarizer import OpenAISummarizer, build_summarization_prompt


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
    run_parser = subparsers.add_parser("run", help="Ingest RSS feeds then list recent articles")
    run_parser.add_argument("--db", required=True, help="Path to SQLite database")
    run_parser.add_argument("--rss", nargs="+", required=True, help="RSS feed URLs")
    run_parser.add_argument("--limit", type=int, default=10, help="Maximum number of articles to show")
    run_parser.add_argument("--source", default=None, help="Filter by source name")
    digest_parser = subparsers.add_parser("digest", help="Generate markdown digest for a given date")
    digest_parser.add_argument("--db", required=True, help="Path to SQLite database")
    digest_parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    digest_parser.add_argument("--out", required=True, help="Output directory for markdown digest")
    summarize_parser = subparsers.add_parser(
        "summarize", help="Generate AI summaries for articles missing them"
    )
    summarize_parser.add_argument("--db", required=True, help="Path to SQLite database")
    summarize_parser.add_argument("--limit", type=int, default=10, help="Maximum number of articles")
    summarize_parser.add_argument("--model", default="gpt-4.1-mini", help="OpenAI model name")
    summarize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Estimate token usage/cost only, without API calls or DB writes",
    )
    summaries_parser = subparsers.add_parser(
        "summaries", help="Show stored AI summaries from the database"
    )
    summaries_parser.add_argument("--db", required=True, help="Path to SQLite database")
    summaries_parser.add_argument("--limit", type=int, default=10, help="Maximum number of summaries")

    return parser


def handler_ingest(args: argparse.Namespace) -> int:
    try:
        session_factory = init_db(args.db)
        items = fetch_rss(args.rss)
        with session_factory() as session:
            nb_new, nb_duplicates = upsert_articles(session, items)
    except Exception as exc:  # noqa: BLE001
        print(f"Ingestion failed: {exc}")
        return 1

    print(f"Total retrieved: {len(items)}")
    print(f"New: {nb_new}")
    print(f"Duplicates: {nb_duplicates}")
    return 0


def handler_list(args: argparse.Namespace) -> int:
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


def handler_run(args: argparse.Namespace) -> int:
    db_parent = Path(args.db).parent
    if str(db_parent) not in ("", "."):
        db_parent.mkdir(parents=True, exist_ok=True)

    print(f"Ingesting feeds into {args.db}...")
    ingest_code = handler_ingest(args)
    if ingest_code != 0:
        return ingest_code

    print("Listing recent articles...")
    return handler_list(args)


def handler_digest(args: argparse.Namespace) -> int:
    try:
        target_date = date.fromisoformat(args.date)
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    session_factory = init_db(args.db)
    with session_factory() as session:
        articles = get_articles_for_date(session, target_date)

    content = render_digest(target_date, articles)
    output_path = out_dir / f"digest_{target_date.isoformat()}.md"
    output_path.write_text(content, encoding="utf-8")
    print(str(output_path))
    return 0


def handler_summarize(args: argparse.Namespace) -> int:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    session_factory = init_db(args.db)
    with session_factory() as session:
        articles = get_articles_missing_ai_summary(session, limit=args.limit)

    if not articles:
        print("No articles to summarize.")
        return 0

    estimated_input_tokens = 0
    expected_output_tokens_total = 0
    estimated_cost_total = 0.0
    for article in articles:
        source_text = article.summary or article.title
        prompt = build_summarization_prompt(article.title, source_text)
        estimated_input_tokens += count_tokens(prompt, model=args.model)
        expected_output_tokens_total += DEFAULT_EXPECTED_OUTPUT_TOKENS
        estimated_cost_total += estimate_api_cost(prompt, model=args.model)

    print(f"Estimated input tokens: {estimated_input_tokens}")
    print(f"Estimated output tokens: {expected_output_tokens_total}")
    print(f"Estimated total tokens: {estimated_input_tokens + expected_output_tokens_total}")
    print(f"Estimated cost (USD): ${estimated_cost_total:.6f}")

    if args.dry_run:
        print("Dry-run enabled: no API calls, no database writes.")
        return 0

    if api_key:
        summarizer = OpenAISummarizer(model=args.model)
    else:
        print("Warning: OPENAI_API_KEY not set. Using MockSummarizer.")
        summarizer = MockSummarizer()

    total = len(articles)
    failures = 0
    for index, article in enumerate(articles, start=1):
        try:
            source_text = article.summary or article.title
            result = summarizer.summarize(article.title, source_text)
            with session_factory() as session:
                save_ai_summary(session, article.id, result["summary"], result["bullets"])
            print(f"[{index}/{total}] summarized article #{article.id}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"[{index}/{total}] failed article #{article.id}: {exc}")

    return 1 if failures else 0


def handler_summaries(args: argparse.Namespace) -> int:
    session_factory = init_db(args.db)
    with session_factory() as session:
        articles = get_recent_articles(session, limit=args.limit)

    with_summaries = [a for a in articles if a.ai_summary_record is not None]
    print(f"Showing {len(with_summaries)} AI summaries")
    if not with_summaries:
        print("No AI summaries found.")
        return 0

    for article in with_summaries:
        record = article.ai_summary_record
        assert record is not None
        print(f"- [{article.id}] {article.title}")
        print(f"  Source: {article.source}")
        print(f"  Summarized at: {record.summarized_at.isoformat()}")
        print(f"  Summary: {record.summary_ai}")
        try:
            bullets = json.loads(record.bullets_ai)
        except json.JSONDecodeError:
            bullets = []
        if isinstance(bullets, list):
            for bullet in bullets:
                print(f"  * {bullet}")
    return 0


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
        return handler_ingest(args)
    if args.command == "list":
        return handler_list(args)
    if args.command == "run":
        return handler_run(args)
    if args.command == "digest":
        return handler_digest(args)
    if args.command == "summarize":
        return handler_summarize(args)
    if args.command == "summaries":
        return handler_summaries(args)

    parser.print_help()
    return 0
