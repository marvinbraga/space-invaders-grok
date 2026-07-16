"""Settings use case — load/save difficulty and theme via SettingsRepository port."""

from __future__ import annotations

from space_invaders.domain.ports import SettingsRepository
from space_invaders.domain.strategies import DifficultyLevel
from space_invaders.domain.value_objects import ThemeId


class SettingsService:
    def __init__(self, repository: SettingsRepository) -> None:
        self._repository = repository

    def load_difficulty(self) -> DifficultyLevel:
        return DifficultyLevel.from_value(self._repository.load_difficulty())

    def save_difficulty(self, level: DifficultyLevel) -> None:
        self._repository.save_difficulty(level.value)

    def load_theme(self) -> ThemeId:
        return ThemeId.from_value(self._repository.load_theme())

    def save_theme(self, theme: ThemeId) -> None:
        self._repository.save_theme(theme.value)
