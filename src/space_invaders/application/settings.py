"""Settings use case — load/save difficulty via SettingsRepository port."""

from __future__ import annotations

from space_invaders.domain.ports import SettingsRepository
from space_invaders.domain.strategies import DifficultyLevel


class SettingsService:
    def __init__(self, repository: SettingsRepository) -> None:
        self._repository = repository

    def load_difficulty(self) -> DifficultyLevel:
        return DifficultyLevel.from_value(self._repository.load_difficulty())

    def save_difficulty(self, level: DifficultyLevel) -> None:
        self._repository.save_difficulty(level.value)
