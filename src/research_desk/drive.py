from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path


def _google_services():
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as error:  # pragma: no cover - exercised in GitHub Actions
        raise RuntimeError("Install the Google extra: pip install -e '.[google]'") from error

    raw_credentials = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw_credentials:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not set.")
    credentials = Credentials.from_service_account_info(json.loads(raw_credentials), scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=credentials), MediaFileUpload


def _escape_query(value: str) -> str:
    return value.replace("'", "\\'")


def _find_or_create_folder(service, name: str, parent_id: str) -> str:
    query = f"name = '{_escape_query(name)}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, spaces="drive", fields="files(id,name)", pageSize=1, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    if results["files"]:
        return results["files"][0]["id"]
    return service.files().create(body={"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}, fields="id", supportsAllDrives=True).execute()["id"]


def _upsert_file(service, media_type, file_path: Path, parent_id: str) -> str:
    query = f"name = '{_escape_query(file_path.name)}' and '{parent_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces="drive", fields="files(id)", pageSize=1, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    media = media_type(str(file_path), resumable=True)
    if results["files"]:
        return service.files().update(fileId=results["files"][0]["id"], media_body=media, fields="id", supportsAllDrives=True).execute()["id"]
    return service.files().create(body={"name": file_path.name, "parents": [parent_id]}, media_body=media, fields="id", supportsAllDrives=True).execute()["id"]


def publish_directory(source_dir: Path, root_folder_id: str, theme: str, now: datetime | None = None) -> dict[str, str | int]:
    """Upload a run into Drive/YYYY-MM-DD/<theme>, replacing files on a retry."""
    if not source_dir.is_dir():
        raise ValueError(f"Output directory does not exist: {source_dir}")
    now = now or datetime.now(UTC)
    service, media_type = _google_services()
    date_folder_id = _find_or_create_folder(service, now.date().isoformat(), root_folder_id)
    theme_folder_id = _find_or_create_folder(service, theme, date_folder_id)
    uploaded = 0
    folder_ids: dict[Path, str] = {source_dir: theme_folder_id}
    for path in sorted(source_dir.rglob("*")):
        parent = folder_ids[path.parent]
        if path.is_dir():
            folder_ids[path] = _find_or_create_folder(service, path.name, parent)
        elif path.is_file():
            _upsert_file(service, media_type, path, parent)
            uploaded += 1
    return {"folder_id": theme_folder_id, "uploaded_files": uploaded}
