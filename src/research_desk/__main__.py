from __future__ import annotations

import argparse
from pathlib import Path

from .render import write_cards
from .us_media import collect


def main() -> None:
    parser = argparse.ArgumentParser(description="Research desk collector")
    parser.add_argument("collect", nargs="?")
    parser.add_argument("--theme", required=True, choices=["us-media", "ai-efficiency", "digital-marketing", "nikkei225", "fx"])
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    if args.theme != "us-media":
        raise SystemExit(f"{args.theme} collector is intentionally gated until its source policy is configured.")
    cards = collect(Path("config/feeds.yaml"))
    manifest = write_cards(cards, Path(args.output_dir))
    print(f"Wrote {len(cards)} cards to {manifest.parent}")


if __name__ == "__main__":
    main()
