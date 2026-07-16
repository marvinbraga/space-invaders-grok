"""File-backed high score repository."""

from __future__ import annotations

import json
from pathlib import Path


class FileScoreRepository:
    """Persists HI-SCORE as JSON on disk."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load_high_score(self) -> int:
        if not self._path.exists():
            return 0
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 0
        if not isinstance(data, dict):
            return 0
        raw = data.get("high_score", 0)
        if isinstance(raw, bool) or not isinstance(raw, int):
            return 0
        return max(0, raw)

    def save_high_score(self, score: int) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"high_score": max(0, int(score))}, indent=2)
        self._path.write_text(payload + "\n", encoding="utf-8")
