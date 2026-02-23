from __future__ import annotations

from datetime import date, datetime, timezone
import json
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .models import Article, ArticleSummary


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO-8601 datetime strings and return None for invalid values."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def upsert_articles(session: Session, articles: list[dict]) -> tuple[int, int]:
    """Insert non-duplicate articles and return (new_count, duplicate_count)."""
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
    """Return the latest stored articles, optionally filtered by source."""
    stmt = select(Article).options(selectinload(Article.ai_summary_record))
    if source:
        stmt = stmt.where(Article.source == source)
    stmt = stmt.order_by(func.coalesce(Article.published, Article.created_at).desc()).limit(limit)
    return list(session.scalars(stmt).all())


def get_articles_for_date(session: Session, date: date) -> list[Article]:
    """Return articles published on a specific calendar date."""
    stmt = (
        select(Article)
        .options(selectinload(Article.ai_summary_record))
        .where(Article.published.is_not(None))
        .where(func.date(Article.published) == date.isoformat())
        .order_by(Article.published.desc(), Article.created_at.desc())
    )
    return list(session.scalars(stmt).all())


def get_articles_missing_ai_summary(session: Session, limit: int = 10) -> list[Article]:
    """Return recent articles that do not have an AI summary record yet."""
    stmt = (
        select(Article)
        .outerjoin(ArticleSummary, ArticleSummary.article_id == Article.id)
        .where(ArticleSummary.id.is_(None))
        .order_by(func.coalesce(Article.published, Article.created_at).desc())
        .limit(limit)
    )
    return list(session.scalars(stmt).all())


def save_ai_summary(session: Session, article_id: int, summary: str, bullets: list[str]) -> None:
    """Create or update the AI summary payload for one article."""
    record = session.scalar(select(ArticleSummary).where(ArticleSummary.article_id == article_id))
    payload = json.dumps(bullets, ensure_ascii=False)
    if record is None:
        record = ArticleSummary(
            article_id=article_id,
            summary_ai=summary,
            bullets_ai=payload,
            summarized_at=datetime.now(timezone.utc),
        )
        session.add(record)
    else:
        record.summary_ai = summary
        record.bullets_ai = payload
        record.summarized_at = datetime.now(timezone.utc)
    session.commit()
