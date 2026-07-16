"""File-backed settings repository (difficulty preference)."""

from __future__ import annotations

import json
from pathlib import Path


class FileSettingsRepository:
    """Persists player settings as JSON on disk."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load_difficulty(self) -> str:
        if not self._path.exists():
            return "hard"
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return "hard"
        if not isinstance(data, dict):
            return "hard"
        raw = data.get("difficulty", "hard")
        if not isinstance(raw, str):
            return "hard"
        return raw

    def save_difficulty(self, difficulty: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        existing: dict[str, object] = {}
        if self._path.exists():
            try:
                loaded = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    existing = loaded
            except (OSError, json.JSONDecodeError):
                existing = {}
        existing["difficulty"] = difficulty
        payload = json.dumps(existing, indent=2)
        self._path.write_text(payload + "\n", encoding="utf-8")
