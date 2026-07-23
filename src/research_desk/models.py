from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class Status(StrEnum):
    INBOX = "取り込み済み"
    PREPARING = "整理・準備中"
    WAITING_NEXT = "次工程待ち"
    VERIFYING = "検証中"
    WAITING_USER = "ユーザー待ち"
    COMPLETE = "完了"
    HOLD = "保留"
    DISCARDED = "破棄"


@dataclass(frozen=True)
class Evidence:
    url: str
    source: str
    title: str
    published_at: str | None
    excerpt: str
    category: str | None = None


@dataclass(frozen=True)
class ResearchCard:
    card_id: str
    theme: str
    status: Status
    priority: float
    headline: str
    evidence: Evidence
    matched_topics: list[str]
    verification_note: str
    next_step: str
    decision_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
