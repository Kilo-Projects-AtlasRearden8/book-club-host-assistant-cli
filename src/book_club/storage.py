"""Local JSON storage for book club data."""

from __future__ import annotations

import json
import os
from typing import Any

from book_club.models import ClubData


class StorageError(Exception):
    """Raised when reading or writing the storage file fails."""


class JSONStorage:
    """Persists ClubData to a single JSON file on disk."""

    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> ClubData:
        if not os.path.exists(self.path):
            return ClubData()
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Unable to read storage file {self.path}: {exc}") from exc
        if not isinstance(data, dict):
            raise StorageError(f"Storage file {self.path} does not contain a JSON object")
        return ClubData.from_dict(data)

    def save(self, club: ClubData) -> None:
        directory = os.path.dirname(os.path.abspath(self.path))
        if directory and not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        tmp_path = f"{self.path}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(club.to_dict(), handle, indent=2, sort_keys=True)
                handle.write("\n")
            os.replace(tmp_path, self.path)
        except OSError as exc:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            raise StorageError(f"Unable to write storage file {self.path}: {exc}") from exc

    @staticmethod
    def default_path() -> str:
        return os.path.join(os.path.expanduser("~"), ".book_club_host.json")
