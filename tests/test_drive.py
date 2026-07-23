from pathlib import Path

from research_desk.drive import publish_directory


def test_missing_output_directory_is_rejected(tmp_path: Path) -> None:
    try:
        publish_directory(tmp_path / "missing", "folder-id", "us-media")
    except ValueError as error:
        assert "does not exist" in str(error)
    else:
        raise AssertionError("Expected a missing output directory error")
