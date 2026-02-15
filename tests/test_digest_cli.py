from robotics_ai_digest.cli import main
from robotics_ai_digest.storage.db import init_db
from robotics_ai_digest.storage.repository import upsert_articles


def test_digest_command_creates_markdown_file(tmp_path):
    db_path = tmp_path / "digest.db"
    out_dir = tmp_path / "out"

    session_factory = init_db(str(db_path))
    with session_factory() as session:
        upsert_articles(
            session,
            [
                {
                    "title": "Digest article",
                    "link": "https://example.com/d1",
                    "guid": "d1",
                    "published": "2025-02-10T09:15:00+00:00",
                    "summary": "Digest summary",
                    "source": "Digest Source",
                }
            ],
        )

    exit_code = main(
        [
            "digest",
            "--db",
            str(db_path),
            "--date",
            "2025-02-10",
            "--out",
            str(out_dir),
        ]
    )

    output_file = out_dir / "digest_2025-02-10.md"
    assert exit_code == 0
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "# Robotics & AI Digest \u2014 2025-02-10" in content
    assert "## Digest Source" in content

