from sqlalchemy import select

from robotics_ai_digest.cli import main
from robotics_ai_digest.storage.models import Article
from robotics_ai_digest.storage.db import init_db
from robotics_ai_digest.storage.repository import save_ai_summary, upsert_articles


def test_summaries_command_displays_saved_summaries(tmp_path, capsys):
    db_path = tmp_path / "digest.db"
    session_factory = init_db(str(db_path))
    with session_factory() as session:
        upsert_articles(
            session,
            [
                {
                    "title": "Stored summary article",
                    "link": "https://example.com/s1",
                    "guid": "gs1",
                    "published": "2025-02-13T10:00:00+00:00",
                    "summary": "rss",
                    "source": "Feed A",
                }
            ],
        )
        article_id = session.scalar(select(Article.id).limit(1))
        assert article_id is not None

    with session_factory() as session:
        save_ai_summary(
            session,
            article_id=article_id,
            summary="AI summary text",
            bullets=["B1", "B2", "B3"],
        )

    exit_code = main(["summaries", "--db", str(db_path), "--limit", "5"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Showing 1 AI summaries" in captured.out
    assert "Stored summary article" in captured.out
    assert "AI summary text" in captured.out
