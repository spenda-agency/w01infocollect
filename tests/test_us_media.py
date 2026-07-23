from datetime import UTC, datetime
from pathlib import Path

from research_desk.us_media import collect


RSS = b'''<?xml version="1.0"?><rss><channel><item><title>Fed signals interest rate change for AI data centers</title><link>https://example.test/a</link><description>Federal Reserve and artificial intelligence</description><pubDate>Wed, 22 Jul 2026 00:00:00 +0000</pubDate></item><item><title>Recipe</title><link>https://example.test/b</link><description>food</description><pubDate>Wed, 22 Jul 2026 00:00:00 +0000</pubDate></item></channel></rss>'''


def test_collect_scores_and_excludes() -> None:
    cards = collect(Path("config/feeds.yaml"), now=datetime(2026, 7, 22, tzinfo=UTC), fetcher=lambda _: RSS)
    assert cards
    assert all(card.evidence.url == "https://example.test/a" for card in cards)
    assert {"AI", "Finance"}.issubset(cards[0].matched_topics)
