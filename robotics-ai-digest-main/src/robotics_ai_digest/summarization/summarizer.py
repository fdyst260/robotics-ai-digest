from __future__ import annotations

from typing import Protocol


class Summarizer(Protocol):
    def summarize(self, title: str, text: str) -> dict:
        """Return {'summary': str, 'bullets': list[str]}."""

