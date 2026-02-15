from __future__ import annotations

from datetime import datetime, timezone
from time import struct_time

import feedparser
import requests


def _to_iso8601(value: struct_time | None) -> str | None:
    if value is None:
        return None
    try:
        dt = datetime(
            value.tm_year,
            value.tm_mon,
            value.tm_mday,
            value.tm_hour,
            value.tm_min,
            value.tm_sec,
            tzinfo=timezone.utc,
        )
        return dt.isoformat()
    except (TypeError, ValueError):
        return None


def fetch_rss(urls: list[str], timeout: int = 15) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()

    for url in urls:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
        except (requests.RequestException, OSError):
            continue

        if getattr(parsed, "bozo", 0):
            continue

        source_name = parsed.feed.get("title", url)
        for entry in parsed.entries:
            guid = entry.get("id") or entry.get("guid") or entry.get("link")
            link = entry.get("link")
            dedupe_key = guid or link
            if dedupe_key and dedupe_key in seen:
                continue
            if dedupe_key:
                seen.add(dedupe_key)

            published = _to_iso8601(entry.get("published_parsed") or entry.get("updated_parsed"))

            items.append(
                {
                    "title": entry.get("title"),
                    "link": link,
                    "published": published,
                    "summary": entry.get("summary") or entry.get("description"),
                    "source": source_name,
                    "guid": guid,
                }
            )

    return items

