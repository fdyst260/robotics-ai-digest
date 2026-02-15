from __future__ import annotations

from collections import OrderedDict
from datetime import date, datetime, timezone
import json

from robotics_ai_digest.storage.models import Article


def _normalize_summary(summary: str | None, max_len: int = 240) -> str | None:
    if not summary:
        return None
    one_line = " ".join(summary.split())
    if len(one_line) <= max_len:
        return one_line
    return f"{one_line[: max_len - 3]}..."


def render_digest(date: date, articles: list[Article]) -> str:
    lines: list[str] = [f"# Robotics & AI Digest \u2014 {date.isoformat()}", ""]

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
            ai_record = article.ai_summary_record
            summary_text = ai_record.summary_ai if ai_record else article.summary
            summary = _normalize_summary(summary_text)
            if summary:
                lines.append(f"  - Summary: {summary}")
            if ai_record and ai_record.bullets_ai:
                try:
                    bullets = json.loads(ai_record.bullets_ai)
                except json.JSONDecodeError:
                    bullets = []
                if isinstance(bullets, list):
                    lines.append("  - Bullets:")
                    for bullet in bullets:
                        lines.append(f"    - {bullet}")
        lines.append("")

    lines.append("---")
    lines.append(f"Total articles: {len(articles)}")
    lines.append(f"Sources count: {len(grouped)}")
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines.append(f"Generated at: {generated_at}")
    lines.append("")

    return "\n".join(lines)
