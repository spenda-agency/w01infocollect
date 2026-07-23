from __future__ import annotations

import hashlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

import yaml

from .models import Evidence, ResearchCard, Status


def _text(value: str | None) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", unescape(value or ""))).strip()


def _published(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(UTC)
    except (TypeError, ValueError):
        return None


def _fetch_xml(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "research-desk/0.1 (+GitHub Actions)"})
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - configured RSS sources
        return response.read()


def _field(item: ET.Element, local_name: str) -> str | None:
    for child in item:
        if child.tag.rsplit("}", 1)[-1] == local_name:
            return child.text
    return None


def _score(text: str, topics: dict) -> tuple[float, list[str]]:
    lower = text.lower()
    matched: list[str] = []
    score = 0.0
    for topic, rule in topics.items():
        hits = sum(keyword.lower() in lower for keyword in rule["keywords"])
        if hits:
            matched.append(topic)
            score += hits * float(rule["weight"])
    return score, matched


def collect(config_path: Path, now: datetime | None = None, fetcher=_fetch_xml) -> list[ResearchCard]:
    now = now or datetime.now(UTC)
    config = yaml.safe_load(config_path.read_text())
    cutoff = float(config["recency_hours_hard_cutoff"])
    exclusions = [value.lower() for value in config["exclude_keywords"]]
    cards: list[ResearchCard] = []

    for source_name, source in config["sources"].items():
        source_cards: list[ResearchCard] = []
        for feed in source["feeds"]:
            try:
                root = ET.fromstring(fetcher(feed["url"]))
            except (ET.ParseError, OSError, TimeoutError):
                continue
            for item in root.findall(".//item"):
                title = _text(_field(item, "title"))
                url = _text(_field(item, "link"))
                excerpt = _text(_field(item, "description"))
                published = _published(_field(item, "pubDate"))
                body = f"{title} {excerpt}".lower()
                if not title or not url or any(word in body for word in exclusions):
                    continue
                if published and (now - published).total_seconds() / 3600 > cutoff:
                    continue
                score, topics = _score(body, config["topics"])
                if score == 0:
                    continue
                card_id = hashlib.sha256(url.encode()).hexdigest()[:12]
                evidence = Evidence(url=url, source=source_name, title=title, published_at=published.isoformat() if published else None, excerpt=excerpt, category=feed["category"])
                source_cards.append(ResearchCard(card_id=card_id, theme="us-media", status=Status.PREPARING, priority=score, headline=title, evidence=evidence, matched_topics=topics, verification_note="RSS記事。本文・一次資料への遷移先は未検証。", next_step="本文を確認し、一次根拠と他テーマへの影響を判定する。"))
        cards.extend(sorted({card.card_id: card for card in source_cards}.values(), key=lambda card: card.priority, reverse=True)[: int(config["per_source_limit"])])
    return sorted(cards, key=lambda card: card.priority, reverse=True)
