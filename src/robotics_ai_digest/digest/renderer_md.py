from __future__ import annotations

from collections import OrderedDict
from datetime import date, datetime

from robotics_ai_digest.storage.models import Article


def _normalize_summary(summary: str | None, max_len: int = 240) -> str | None:
    if not summary:
        return None
    one_line = " ".join(summary.split())
    if len(one_line) <= max_len:
        return one_line
    return f"{one_line[: max_len - 3]}..."


def render_digest(date: date, articles: list[Article]) -> str:
    lines: list[str] = [f"# Robotics & AI Digest — {date.isoformat()}", ""]

    grouped: OrderedDict[str, list[Article]] = OrderedDict()
    for article in articles:
        grouped.setdefault(article.source, []).append(article)

    for source, source_articles in grouped.items():
        lines.append(f"## {source}")
        lines.append("")
        for article in source_articles:
            title = article.title or "(untitled)"
            lines.append(f"- **[{title}]({article.link})**")
            if article.published:
                lines.append(f"  - Published: {article.published.strftime('%Y-%m-%d %H:%M')}")
            summary = _normalize_summary(article.summary)
            if summary:
                lines.append(f"  - Summary: {summary}")
        lines.append("")

    lines.append("---")
    lines.append(f"Total articles: {len(articles)}")
    lines.append(f"Number of sources: {len(grouped)}")
    lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    return "\n".join(lines)

