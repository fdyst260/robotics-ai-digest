from sqlalchemy import select

from robotics_ai_digest.cli import main
from robotics_ai_digest.storage.db import init_db
from robotics_ai_digest.storage.models import ArticleSummary
from robotics_ai_digest.storage.repository import upsert_articles
from robotics_ai_digest.summarization.openai_summarizer import OpenAISummarizer


def test_summarize_command_uses_mock_and_persists(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("robotics_ai_digest.cli.load_dotenv", lambda: None)

    db_path = tmp_path / "digest.db"
    session_factory = init_db(str(db_path))
    with session_factory() as session:
        upsert_articles(
            session,
            [
                {
                    "title": "A1",
                    "link": "https://example.com/a1",
                    "guid": "ga1",
                    "published": "2025-02-12T10:00:00+00:00",
                    "summary": "rss a1",
                    "source": "Feed A",
                },
                {
                    "title": "A2",
                    "link": "https://example.com/a2",
                    "guid": "ga2",
                    "published": "2025-02-12T11:00:00+00:00",
                    "summary": "rss a2",
                    "source": "Feed A",
                },
            ],
        )

    exit_code = main(["summarize", "--db", str(db_path), "--limit", "5"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Warning: OPENAI_API_KEY not set. Using MockSummarizer." in captured.out
    assert "summarized article" in captured.out

    with session_factory() as session:
        rows = session.scalars(select(ArticleSummary)).all()
    assert len(rows) == 2


def test_summarize_dry_run_estimates_without_api_or_db_write(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def should_not_be_called(self, title, text):  # noqa: ANN001, ANN202
        raise AssertionError("OpenAI summarizer should not be called in dry-run")

    monkeypatch.setattr(OpenAISummarizer, "summarize", should_not_be_called)

    db_path = tmp_path / "dry_run.db"
    session_factory = init_db(str(db_path))
    with session_factory() as session:
        upsert_articles(
            session,
            [
                {
                    "title": "Dry run article",
                    "link": "https://example.com/dry",
                    "guid": "gdry",
                    "published": "2025-02-12T10:00:00+00:00",
                    "summary": "rss dry",
                    "source": "Feed A",
                }
            ],
        )

    exit_code = main(["summarize", "--db", str(db_path), "--limit", "1", "--dry-run"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Estimated input tokens:" in captured.out
    assert "Estimated cost (USD):" in captured.out
    assert "Dry-run enabled: no API calls, no database writes." in captured.out

    with session_factory() as session:
        rows = session.scalars(select(ArticleSummary)).all()
    assert len(rows) == 0
