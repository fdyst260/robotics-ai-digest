from __future__ import annotations

import json

from openai import OpenAI

from .summarizer import Summarizer


class OpenAISummarizer(Summarizer):
    def __init__(self, model: str = "gpt-4.1-mini"):
        self.model = model
        self.client = OpenAI()

    def summarize(self, title: str, text: str) -> dict:
        instructions = (
            "Tu es un assistant de veille robotique/IA. "
            "Réponds en JSON strict avec les clés 'summary' et 'bullets'. "
            "Le résumé doit être neutre, factuel, en français, entre 80 et 120 mots. "
            "Donne exactement 3 puces dans 'bullets'."
        )
        payload = f"Title: {title}\n\nContent:\n{text}"

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=payload,
            )
            content = response.output_text
            result = json.loads(content)
            summary = result.get("summary")
            bullets = result.get("bullets")
            if not isinstance(summary, str) or not isinstance(bullets, list):
                raise ValueError("Invalid OpenAI response format")
            return {"summary": summary, "bullets": [str(item) for item in bullets][:3]}
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"OpenAI summarization failed: {exc}") from exc

