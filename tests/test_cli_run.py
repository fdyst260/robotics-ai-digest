from robotics_ai_digest.cli import main
from robotics_ai_digest.storage.db import init_db
from robotics_ai_digest.storage.repository import get_recent_articles


def test_run_command_ingests_and_lists(capsys, tmp_path, monkeypatch):
    articles = [
        {
            "title": "Robot One",
            "link": "https://example.com/one",
            "guid": "g1",
            "published": "2025-02-10T10:00:00+00:00",
            "summary": "s1",
            "source": "Feed A",
        },
        {
            "title": "Robot Two",
            "link": "https://example.com/two",
            "guid": "g2",
            "published": "2025-02-11T10:00:00+00:00",
            "summary": "s2",
            "source": "Feed A",
        },
        {
            "title": "Robot Three",
            "link": "https://example.com/three",
            "guid": "g3",
            "published": "2025-02-12T10:00:00+00:00",
            "summary": "s3",
            "source": "Feed B",
        },
    ]

    def fake_fetch_rss(urls):  # noqa: ANN001, ANN202
        return articles

    monkeypatch.setattr("robotics_ai_digest.cli.fetch_rss", fake_fetch_rss)

    db_path = tmp_path / "nested" / "digest.db"
    exit_code = main(
        [
            "run",
            "--db",
            str(db_path),
            "--rss",
            "https://example.com/rss.xml",
            "--limit",
            "2",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Ingesting feeds into" in captured.out
    assert "Listing recent articles..." in captured.out

    session_factory = init_db(str(db_path))
    with session_factory() as session:
        stored = get_recent_articles(session, limit=10)
    assert len(stored) == 3


def test_run_command_applies_source_filter(capsys, tmp_path, monkeypatch):
    articles = [
        {
            "title": "From A",
            "link": "https://example.com/a",
            "guid": "ga",
            "published": "2025-02-10T10:00:00+00:00",
            "summary": "a",
            "source": "Feed A",
        },
        {
            "title": "From B",
            "link": "https://example.com/b",
            "guid": "gb",
            "published": "2025-02-11T10:00:00+00:00",
            "summary": "b",
            "source": "Feed B",
        },
    ]

    def fake_fetch_rss(urls):  # noqa: ANN001, ANN202
        return articles

    monkeypatch.setattr("robotics_ai_digest.cli.fetch_rss", fake_fetch_rss)

    db_path = tmp_path / "digest.db"
    exit_code = main(
        [
            "run",
            "--db",
            str(db_path),
            "--rss",
            "https://example.com/rss.xml",
            "--source",
            "Feed A",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "[2025-02-10] Feed A" in captured.out
    assert "From A" in captured.out
    assert "From B" not in captured.out

