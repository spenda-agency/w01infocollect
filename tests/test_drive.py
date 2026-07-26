from pathlib import Path

from research_desk.drive import _find_or_create_folder, _upsert_file, publish_directory


def test_missing_output_directory_is_rejected(tmp_path: Path) -> None:
    try:
        publish_directory(tmp_path / "missing", "folder-id", "us-media")
    except ValueError as error:
        assert "does not exist" in str(error)
    else:
        raise AssertionError("Expected a missing output directory error")


class _Recorder:
    """Minimal stand-in for the Drive files() resource that records call kwargs."""

    def __init__(self, list_files):
        self._list_files = list_files
        self.calls: list[tuple[str, dict]] = []

    def files(self):
        return self

    def list(self, **kwargs):
        self.calls.append(("list", kwargs))
        return _Execute({"files": self._list_files})

    def create(self, **kwargs):
        self.calls.append(("create", kwargs))
        return _Execute({"id": "created-id"})

    def update(self, **kwargs):
        self.calls.append(("update", kwargs))
        return _Execute({"id": "updated-id"})


class _Execute:
    def __init__(self, payload):
        self._payload = payload

    def execute(self):
        return self._payload


def test_find_or_create_folder_supports_shared_drives() -> None:
    service = _Recorder(list_files=[])
    _find_or_create_folder(service, "2026-07-26", "root-id")
    list_kwargs = dict(service.calls[0][1])
    create_kwargs = dict(service.calls[1][1])
    assert list_kwargs["supportsAllDrives"] is True
    assert list_kwargs["includeItemsFromAllDrives"] is True
    assert create_kwargs["supportsAllDrives"] is True


def test_upsert_file_supports_shared_drives(tmp_path: Path) -> None:
    target = tmp_path / "manifest.json"
    target.write_text("{}", encoding="utf-8")
    service = _Recorder(list_files=[{"id": "existing"}])
    _upsert_file(service, drive_media_stub, target, "parent-id")
    list_kwargs = dict(service.calls[0][1])
    update_kwargs = dict(service.calls[1][1])
    assert list_kwargs["supportsAllDrives"] is True
    assert list_kwargs["includeItemsFromAllDrives"] is True
    assert update_kwargs["supportsAllDrives"] is True


def drive_media_stub(path, resumable=False):
    return {"path": path, "resumable": resumable}
