from datetime import date

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from robotics_ai_digest.storage.models import Article, Base
from robotics_ai_digest.storage.repository import (
    get_articles_for_date,
    get_articles_missing_ai_summary,
    get_recent_articles,
    save_ai_summary,
    upsert_articles,
)


def test_upsert_articles_does_not_insert_duplicate():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)

    articles = [
        {
            "title": "A1",
            "link": "https://example.com/a1",
            "guid": "guid-a1",
            "published": "2025-01-01T10:00:00+00:00",
            "summary": "s1",
            "source": "feed",
        },
        {
            "title": "A1 duplicate",
            "link": "https://example.com/a1",
            "guid": "guid-a1",
            "published": "2025-01-01T10:00:00+00:00",
            "summary": "s1 dup",
            "source": "feed",
        },
    ]

    with session_factory() as session:
        nb_new, nb_duplicates = upsert_articles(session, articles)
        count = session.scalar(select(func.count()).select_from(Article))

    assert nb_new == 1
    assert nb_duplicates == 1
    assert count == 1


def test_get_recent_articles_respects_limit():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)

    articles = [
        {
            "title": "Older",
            "link": "https://example.com/old",
            "guid": "g-old",
            "published": "2025-01-01T10:00:00+00:00",
            "summary": "old",
            "source": "Feed A",
        },
        {
            "title": "Middle",
            "link": "https://example.com/mid",
            "guid": "g-mid",
            "published": "2025-01-02T10:00:00+00:00",
            "summary": "mid",
            "source": "Feed A",
        },
        {
            "title": "Newest",
            "link": "https://example.com/new",
            "guid": "g-new",
            "published": "2025-01-03T10:00:00+00:00",
            "summary": "new",
            "source": "Feed A",
        },
    ]

    with session_factory() as session:
        upsert_articles(session, articles)
        recent = get_recent_articles(session, limit=2)

    assert len(recent) == 2
    assert [article.title for article in recent] == ["Newest", "Middle"]


def test_get_recent_articles_filters_by_source():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)

    articles = [
        {
            "title": "From A",
            "link": "https://example.com/a",
            "guid": "g-a",
            "published": "2025-01-01T10:00:00+00:00",
            "summary": "a",
            "source": "Feed A",
        },
        {
            "title": "From B",
            "link": "https://example.com/b",
            "guid": "g-b",
            "published": "2025-01-02T10:00:00+00:00",
            "summary": "b",
            "source": "Feed B",
        },
    ]

    with session_factory() as session:
        upsert_articles(session, articles)
        only_a = get_recent_articles(session, source="Feed A")

    assert len(only_a) == 1
    assert only_a[0].title == "From A"


def test_get_articles_for_date_returns_only_matching_published_day():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)

    articles = [
        {
            "title": "Target date",
            "link": "https://example.com/target",
            "guid": "g-target",
            "published": "2025-02-10T08:00:00+00:00",
            "summary": "target",
            "source": "Feed A",
        },
        {
            "title": "Other date",
            "link": "https://example.com/other",
            "guid": "g-other",
            "published": "2025-02-11T08:00:00+00:00",
            "summary": "other",
            "source": "Feed A",
        },
        {
            "title": "No published",
            "link": "https://example.com/none",
            "guid": "g-none",
            "published": None,
            "summary": "none",
            "source": "Feed A",
        },
    ]

    with session_factory() as session:
        upsert_articles(session, articles)
        selected = get_articles_for_date(session, date(2025, 2, 10))

    assert len(selected) == 1
    assert selected[0].title == "Target date"


def test_save_ai_summary_updates_missing_query():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)

    with session_factory() as session:
        upsert_articles(
            session,
            [
                {
                    "title": "Needs summary",
                    "link": "https://example.com/needs",
                    "guid": "g-needs",
                    "published": "2025-02-12T08:00:00+00:00",
                    "summary": "rss",
                    "source": "Feed A",
                }
            ],
        )
        missing = get_articles_missing_ai_summary(session, limit=10)
        assert len(missing) == 1
        article_id = missing[0].id

    with session_factory() as session:
        save_ai_summary(session, article_id, "AI summary", ["b1", "b2", "b3"])
        missing_after = get_articles_missing_ai_summary(session, limit=10)
        assert missing_after == []
