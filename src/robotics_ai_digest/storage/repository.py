from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Article


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def upsert_articles(session: Session, articles: list[dict]) -> tuple[int, int]:
    if not articles:
        return 0, 0

    links = [item.get("link") for item in articles if item.get("link")]
    guids = [item.get("guid") for item in articles if item.get("guid")]

    existing_links = set(session.scalars(select(Article.link).where(Article.link.in_(links))).all())
    existing_guids = set(session.scalars(select(Article.guid).where(Article.guid.in_(guids))).all())

    new_count = 0
    duplicate_count = 0
    seen_links = set(existing_links)
    seen_guids = set(existing_guids)

    for item in articles:
        link = item.get("link")
        guid = item.get("guid")
        if not link:
            continue
        if link in seen_links or (guid and guid in seen_guids):
            duplicate_count += 1
            continue

        article = Article(
            title=item.get("title") or "(untitled)",
            link=link,
            guid=guid,
            published=_parse_datetime(item.get("published")),
            summary=item.get("summary"),
            source=item.get("source") or "unknown",
        )
        session.add(article)
        seen_links.add(link)
        if guid:
            seen_guids.add(guid)
        new_count += 1

    session.commit()
    return new_count, duplicate_count


def get_recent_articles(
    session: Session, limit: int = 10, source: Optional[str] = None
) -> list[Article]:
    stmt = select(Article)
    if source:
        stmt = stmt.where(Article.source == source)
    stmt = stmt.order_by(func.coalesce(Article.published, Article.created_at).desc()).limit(limit)
    return list(session.scalars(stmt).all())


def get_articles_for_date(session: Session, date: date) -> list[Article]:
    stmt = (
        select(Article)
        .where(Article.published.is_not(None))
        .where(func.date(Article.published) == date.isoformat())
        .order_by(Article.published.desc(), Article.created_at.desc())
    )
    return list(session.scalars(stmt).all())
