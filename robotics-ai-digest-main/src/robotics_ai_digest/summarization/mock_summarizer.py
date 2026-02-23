from __future__ import annotations

from .summarizer import Summarizer


class MockSummarizer(Summarizer):
    """Deterministic local summarizer used for tests and no-key scenarios."""

    def summarize(self, title: str, text: str) -> dict:
        lowered = title.lower().strip()
        return {
            "summary": (
                f"Mock summary: the article '{title}' highlights key robotics and AI points. "
                f"This output is generated locally for tests without external API calls ({lowered})."
            ),
            "bullets": [
                f"Main context: {title}",
                "Technical points generated automatically",
                "Confidence level: mock mode",
            ],
        }
