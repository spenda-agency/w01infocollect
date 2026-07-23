from pathlib import Path

import yaml


def test_fx_pairs_are_unique_and_complete() -> None:
    pairs = yaml.safe_load(Path("config/fx_pairs.yaml").read_text())["pairs"]
    assert len(pairs) == 69
    assert len(pairs) == len(set(pairs))
    assert "USDJPY" in pairs
    assert "AUDNZD" in pairs


def test_nikkei_universe_requires_a_dated_source() -> None:
    universe = yaml.safe_load(Path("config/nikkei225.yaml").read_text())
    assert universe["constituents"] == []
    assert universe["as_of"] is None
