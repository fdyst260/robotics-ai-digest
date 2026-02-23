from pathlib import Path

from robotics_ai_digest.feeds.rss_reader import fetch_rss


class DummyResponse:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")


def test_fetch_rss_parses_feed_and_deduplicates(monkeypatch):
    fixture_path = Path(__file__).parent / "fixtures" / "sample_rss.xml"
    xml_bytes = fixture_path.read_bytes()

    def fake_get(url, timeout):  # noqa: ANN001, ANN202
        return DummyResponse(xml_bytes)

    monkeypatch.setattr("robotics_ai_digest.feeds.rss_reader.requests.get", fake_get)

    items = fetch_rss(["https://example.com/rss.xml"])

    assert len(items) == 2
    assert items[0]["title"] == "Robot Alpha"
    assert items[0]["guid"] == "alpha-1"
    assert items[0]["source"] == "Robotics News"
    assert items[0]["published"] == "2025-02-10T10:00:00+00:00"
    assert items[1]["title"] == "Robot Beta"
    assert items[1]["guid"] == "https://example.com/beta"


def test_fetch_rss_invalid_feed_returns_empty_list(monkeypatch):
    def fake_get(url, timeout):  # noqa: ANN001, ANN202
        return DummyResponse(b"not-an-rss-feed")

    monkeypatch.setattr("robotics_ai_digest.feeds.rss_reader.requests.get", fake_get)

    items = fetch_rss(["https://example.com/invalid.xml"])

    assert items == []

