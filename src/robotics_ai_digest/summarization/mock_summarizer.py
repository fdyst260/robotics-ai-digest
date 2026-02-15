from __future__ import annotations

from .summarizer import Summarizer


class MockSummarizer(Summarizer):
    def summarize(self, title: str, text: str) -> dict:
        lowered = title.lower().strip()
        return {
            "summary": f"Résumé mock: l'article '{title}' présente les points clés en robotique/IA."
            f" Ce contenu est généré localement pour tests sans API externe ({lowered}).",
            "bullets": [
                f"Contexte principal: {title}",
                "Points techniques synthétisés automatiquement",
                "Niveau de confiance: mode mock",
            ],
        }

