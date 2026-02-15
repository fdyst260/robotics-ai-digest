from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from robotics_ai_digest.storage.models import Article, Base
from robotics_ai_digest.storage.repository import get_recent_articles, upsert_articles


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
