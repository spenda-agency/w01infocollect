from __future__ import annotations

import json
from pathlib import Path

from .models import ResearchCard


def write_cards(cards: list[ResearchCard], output_dir: Path) -> Path:
    cards_dir = output_dir / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for card in cards:
        path = cards_dir / f"{card.card_id}.md"
        evidence = card.evidence
        path.write_text(f"# {card.headline}\n\n- テーマ: {card.theme}\n- 状態: {card.status}\n- 優先度: {card.priority}\n- ソース: {evidence.source} / {evidence.category or '-'}\n- 公開日時: {evidence.published_at or '不明'}\n- 原典: {evidence.url}\n\n## RSS要約\n\n{evidence.excerpt or '要約なし'}\n\n## 検証\n\n{card.verification_note}\n\n## 次の節目\n\n{card.next_step}\n\n## 判定\n\n- 候補: 未判定\n- 判断理由: {card.decision_reason or '未記録'}\n", encoding="utf-8")
        manifest.append(card.to_dict())
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path
