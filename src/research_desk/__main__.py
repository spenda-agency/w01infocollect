from __future__ import annotations

import argparse
import os
from pathlib import Path

from .drive import publish_directory
from .render import write_cards
from .us_media import collect


def main() -> None:
    parser = argparse.ArgumentParser(description="Research desk collector")
    parser.add_argument("command", choices=["collect", "publish-drive"])
    parser.add_argument("--theme", required=True, choices=["us-media", "ai-efficiency", "digital-marketing", "nikkei225", "fx"])
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if args.command == "collect":
        if args.theme != "us-media":
            raise SystemExit(f"{args.theme} collector is intentionally gated until its source policy is configured.")
        cards = collect(Path("config/feeds.yaml"))
        manifest = write_cards(cards, output_dir)
        print(f"Wrote {len(cards)} cards to {manifest.parent}")
        return
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        raise SystemExit("GOOGLE_DRIVE_FOLDER_ID is not set.")
    result = publish_directory(output_dir, folder_id, args.theme)
    print(f"Uploaded {result['uploaded_files']} files to Drive folder {result['folder_id']}")


if __name__ == "__main__":
    main()
