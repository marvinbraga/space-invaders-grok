"""File-backed settings repository (difficulty + theme preferences)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

_DEFAULT_DIFFICULTY: Final[str] = "hard"
_DEFAULT_THEME: Final[str] = "classic"


class FileSettingsRepository:
    """Persists player settings as JSON on disk."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load_difficulty(self) -> str:
        return self._load_string("difficulty", _DEFAULT_DIFFICULTY)

    def save_difficulty(self, difficulty: str) -> None:
        self._save_key("difficulty", difficulty)

    def load_theme(self) -> str:
        return self._load_string("theme", _DEFAULT_THEME)

    def save_theme(self, theme: str) -> None:
        self._save_key("theme", theme)

    def _load_string(self, key: str, default: str) -> str:
        data = self._read_dict()
        if data is None:
            return default
        raw = data.get(key, default)
        if not isinstance(raw, str):
            return default
        return raw

    def _save_key(self, key: str, value: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        existing = self._read_dict() or {}
        existing[key] = value
        payload = json.dumps(existing, indent=2)
        self._path.write_text(payload + "\n", encoding="utf-8")

    def _read_dict(self) -> dict[str, object] | None:
        if not self._path.exists():
            return None
        try:
            loaded = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(loaded, dict):
            return None
        return loaded
