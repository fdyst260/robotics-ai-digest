from datetime import date, datetime, timezone

from robotics_ai_digest.digest.renderer_md import render_digest
from robotics_ai_digest.storage.models import Article, ArticleSummary


def test_render_digest_groups_by_source_and_uses_markdown_links():
    articles = [
        Article(
            title="Article A1",
            link="https://example.com/a1",
            guid="a1",
            published=datetime(2025, 2, 10, 10, 30, tzinfo=timezone.utc),
            summary="Summary A1",
            source="Source A",
        ),
        Article(
            title="Article B1",
            link="https://example.com/b1",
            guid="b1",
            published=datetime(2025, 2, 10, 11, 0, tzinfo=timezone.utc),
            summary="Summary B1",
            source="Source B",
        ),
    ]

    output = render_digest(date(2025, 2, 10), articles)

    assert "# Robotics & AI Digest \u2014 2025-02-10" in output
    assert "## Source A" in output
    assert "## Source B" in output
    assert "- **[Article A1](https://example.com/a1)**" in output
    assert "- **[Article B1](https://example.com/b1)**" in output
    assert "Total articles: 2" in output
    assert "Sources count: 2" in output
    assert "Generated at: " in output


def test_render_digest_prefers_ai_summary_and_shows_bullets():
    article = Article(
        title="AI Article",
        link="https://example.com/ai",
        guid="ai-1",
        published=datetime(2025, 2, 10, 12, 0, tzinfo=timezone.utc),
        summary="RSS summary should be replaced",
        source="Source AI",
    )
    article.ai_summary_record = ArticleSummary(
        article_id=1,
        summary_ai="AI summary selected",
        bullets_ai='["Point A","Point B","Point C"]',
        summarized_at=datetime(2025, 2, 10, 13, 0, tzinfo=timezone.utc),
    )

    output = render_digest(date(2025, 2, 10), [article])

    assert "Summary: AI summary selected" in output
    assert "RSS summary should be replaced" not in output
    assert "  - Bullets:" in output
    assert "    - Point A" in output
