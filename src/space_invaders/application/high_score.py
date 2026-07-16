"""High-score use case — wires ScoreRepository port."""

from __future__ import annotations

from space_invaders.domain.ports import ScoreRepository
from space_invaders.domain.value_objects import MAX_HI_SCORE


class HighScoreService:
    """Load and persist HI-SCORE through the score port.

    Compares candidates against the *stored* value, not only the in-memory
    session high (which is often already updated during play).
    """

    def __init__(self, repository: ScoreRepository) -> None:
        self._repository = repository
        self._stored: int | None = None

    def load(self) -> int:
        raw = self._repository.load_high_score()
        value = 0 if raw < 0 else min(raw, MAX_HI_SCORE)
        self._stored = value
        return value

    def save_if_higher(self, score: int, current_high: int) -> int:
        """Persist when max(score, current_high) beats disk; return effective high."""
        candidate = max(0, score, current_high)
        candidate = min(candidate, MAX_HI_SCORE)
        stored = self._stored if self._stored is not None else self.load()
        if candidate > stored:
            self._repository.save_high_score(candidate)
            self._stored = candidate
            return candidate
        return stored

    def force_save(self, score: int) -> None:
        clamped = max(0, min(score, MAX_HI_SCORE))
        self._repository.save_high_score(clamped)
        self._stored = clamped
