from robotics_ai_digest.cli import main


def test_version_command(capsys):
    exit_code = main(["version"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.strip() == "0.1.0"


def test_ingest_command_outputs_counts(capsys, tmp_path, monkeypatch):
    articles = [
        {
            "title": "One",
            "link": "https://example.com/1",
            "guid": "g1",
            "published": "2025-02-10T10:00:00+00:00",
            "summary": "s1",
            "source": "Feed A",
        },
        {
            "title": "One duplicate",
            "link": "https://example.com/1",
            "guid": "g1",
            "published": "2025-02-10T10:00:00+00:00",
            "summary": "s1 dup",
            "source": "Feed A",
        },
    ]

    def fake_fetch_rss(urls):  # noqa: ANN001, ANN202
        return articles

    monkeypatch.setattr("robotics_ai_digest.cli.fetch_rss", fake_fetch_rss)

    db_path = tmp_path / "digest.db"
    exit_code = main(["ingest", "--db", str(db_path), "--rss", "https://example.com/rss.xml"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Total retrieved: 2" in captured.out
    assert "New: 1" in captured.out
    assert "Duplicates: 1" in captured.out


def test_list_command_handles_empty_database(capsys, tmp_path):
    db_path = tmp_path / "empty.db"
    exit_code = main(["list", "--db", str(db_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Showing 0 most recent articles" in captured.out
    assert "No articles found." in captured.out
