"""Movement / difficulty strategies by wave and player-selected level (Strategy)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final, Protocol

from space_invaders.domain.constants import (
    ALIEN_BULLET_SPEED,
    BASE_ALIEN_FIRE_INTERVAL,
    BASE_STEP_INTERVAL,
    MIN_ALIEN_FIRE_INTERVAL,
    MIN_STEP_INTERVAL,
    UFO_SPEED,
)


class DifficultyLevel(Enum):
    """Player-selectable global difficulty (Settings menu)."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

    @property
    def label(self) -> str:
        return _LABELS[self]

    @classmethod
    def ordered(cls) -> tuple[DifficultyLevel, ...]:
        return (cls.EASY, cls.MEDIUM, cls.HARD, cls.VERY_HARD)

    @classmethod
    def from_value(cls, raw: str) -> DifficultyLevel:
        try:
            return cls(raw)
        except ValueError:
            return cls.HARD


_LABELS: Final[dict[DifficultyLevel, str]] = {
    DifficultyLevel.EASY: "FACIL",
    DifficultyLevel.MEDIUM: "MEDIO",
    DifficultyLevel.HARD: "DIFICIL",
    DifficultyLevel.VERY_HARD: "DIFICILIMO",
}


@dataclass(frozen=True, slots=True)
class DifficultyProfile:
    """Scales classic wave difficulty. Higher step/fire scale = easier."""

    step_scale: float
    fire_scale: float
    bullet_speed_scale: float
    max_bullets_base: int
    max_bullets_cap: int
    wave_step_rate: float
    wave_fire_rate: float
    endgame_hard: float  # lower = faster endgame (harder)


_PROFILES: Final[dict[DifficultyLevel, DifficultyProfile]] = {
    DifficultyLevel.EASY: DifficultyProfile(
        step_scale=1.55,
        fire_scale=1.75,
        bullet_speed_scale=0.72,
        max_bullets_base=1,
        max_bullets_cap=3,
        wave_step_rate=0.10,
        wave_fire_rate=0.12,
        endgame_hard=1.35,
    ),
    DifficultyLevel.MEDIUM: DifficultyProfile(
        step_scale=1.22,
        fire_scale=1.30,
        bullet_speed_scale=0.88,
        max_bullets_base=2,
        max_bullets_cap=4,
        wave_step_rate=0.15,
        wave_fire_rate=0.20,
        endgame_hard=1.10,
    ),
    # Baseline = current arcade balance
    DifficultyLevel.HARD: DifficultyProfile(
        step_scale=1.0,
        fire_scale=1.0,
        bullet_speed_scale=1.0,
        max_bullets_base=3,
        max_bullets_cap=6,
        wave_step_rate=0.22,
        wave_fire_rate=0.30,
        endgame_hard=1.0,
    ),
    DifficultyLevel.VERY_HARD: DifficultyProfile(
        step_scale=0.80,
        fire_scale=0.72,
        bullet_speed_scale=1.18,
        max_bullets_base=4,
        max_bullets_cap=7,
        wave_step_rate=0.28,
        wave_fire_rate=0.36,
        endgame_hard=0.85,
    ),
}


class DifficultyStrategy(Protocol):
    """Encapsulates wave-dependent timing parameters."""

    def step_interval(self, alive_count: int, total: int) -> float: ...

    def alien_fire_interval(self) -> float: ...

    def ufo_speed(self) -> float: ...

    def max_alien_bullets(self) -> int: ...

    def alien_bullet_speed(self) -> float: ...


class WaveDifficulty:
    """Progressive difficulty scaled by wave number, remaining aliens, and level."""

    def __init__(self, wave: int, level: DifficultyLevel = DifficultyLevel.HARD) -> None:
        if wave < 1:
            msg = f"Wave must be >= 1, got {wave}"
            raise ValueError(msg)
        self._wave = wave
        self._level = level
        self._profile = _PROFILES[level]
        profile = self._profile
        self._wave_factor = 1.0 / (1.0 + profile.wave_step_rate * (wave - 1))
        self._fire_factor = 1.0 / (1.0 + profile.wave_fire_rate * (wave - 1))

    @property
    def wave(self) -> int:
        return self._wave

    @property
    def level(self) -> DifficultyLevel:
        return self._level

    def step_interval(self, alive_count: int, total: int) -> float:
        if total <= 0:
            return MIN_STEP_INTERVAL
        ratio = alive_count / total
        base = BASE_STEP_INTERVAL * self._profile.step_scale * self._wave_factor
        hard = self._profile.endgame_hard
        if alive_count <= 1:
            return MIN_STEP_INTERVAL
        if alive_count <= 3:
            return max(MIN_STEP_INTERVAL, base * 0.06 * hard)
        if alive_count <= 8:
            return max(MIN_STEP_INTERVAL, base * 0.14 * hard)
        if alive_count <= 15:
            return max(MIN_STEP_INTERVAL, base * 0.24 * hard)
        if alive_count <= 25:
            return max(MIN_STEP_INTERVAL, base * 0.40 * hard)
        return max(MIN_STEP_INTERVAL, base * (0.22 + 0.78 * ratio))

    def alien_fire_interval(self) -> float:
        interval = BASE_ALIEN_FIRE_INTERVAL * self._profile.fire_scale * self._fire_factor
        return max(MIN_ALIEN_FIRE_INTERVAL, interval)

    def ufo_speed(self) -> float:
        return UFO_SPEED * (1.0 + 0.10 * (self._wave - 1)) * (2.0 - self._profile.step_scale * 0.5)

    def max_alien_bullets(self) -> int:
        profile = self._profile
        return min(profile.max_bullets_cap, profile.max_bullets_base + (self._wave - 1))

    def alien_bullet_speed(self) -> float:
        return ALIEN_BULLET_SPEED * self._profile.bullet_speed_scale


def difficulty_for_wave(
    wave: int,
    level: DifficultyLevel = DifficultyLevel.HARD,
) -> DifficultyStrategy:
    return WaveDifficulty(wave, level)


def profile_for(level: DifficultyLevel) -> DifficultyProfile:
    return _PROFILES[level]
