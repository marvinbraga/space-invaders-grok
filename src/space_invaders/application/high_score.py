"""High-score use case — wires ScoreRepository port."""

from __future__ import annotations

from space_invaders.domain.ports import ScoreRepository
from space_invaders.domain.value_objects import MAX_HI_SCORE


class HighScoreService:
    """Load and persist HI-SCORE through the score port."""

    def __init__(self, repository: ScoreRepository) -> None:
        self._repository = repository

    def load(self) -> int:
        raw = self._repository.load_high_score()
        if raw < 0:
            return 0
        return min(raw, MAX_HI_SCORE)

    def save_if_higher(self, score: int, current_high: int) -> int:
        """Persist when score beats current high; return the new high."""
        if score < 0:
            return current_high
        best = max(current_high, score)
        best = min(best, MAX_HI_SCORE)
        if best > current_high:
            self._repository.save_high_score(best)
        return best

    def force_save(self, score: int) -> None:
        clamped = max(0, min(score, MAX_HI_SCORE))
        self._repository.save_high_score(clamped)
