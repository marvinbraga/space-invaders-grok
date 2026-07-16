"""Movement / difficulty strategies by wave (Strategy pattern)."""

from __future__ import annotations

from typing import Protocol

from space_invaders.domain.constants import (
    BASE_ALIEN_FIRE_INTERVAL,
    BASE_STEP_INTERVAL,
    MIN_ALIEN_FIRE_INTERVAL,
    MIN_STEP_INTERVAL,
    UFO_SPEED,
)


class DifficultyStrategy(Protocol):
    """Encapsulates wave-dependent timing parameters."""

    def step_interval(self, alive_count: int, total: int) -> float: ...

    def alien_fire_interval(self) -> float: ...

    def ufo_speed(self) -> float: ...

    def max_alien_bullets(self) -> int: ...


class WaveDifficulty:
    """Progressive difficulty scaled by wave number and remaining aliens."""

    def __init__(self, wave: int) -> None:
        if wave < 1:
            msg = f"Wave must be >= 1, got {wave}"
            raise ValueError(msg)
        self._wave = wave
        # Steep wave ramp: ~18% faster march and denser fire per wave
        self._wave_factor = 1.0 / (1.0 + 0.18 * (wave - 1))
        self._fire_factor = 1.0 / (1.0 + 0.25 * (wave - 1))

    @property
    def wave(self) -> int:
        return self._wave

    def step_interval(self, alive_count: int, total: int) -> float:
        if total <= 0:
            return MIN_STEP_INTERVAL
        ratio = alive_count / total
        # Classic feel: interval shrinks nonlinearly as aliens die
        base = BASE_STEP_INTERVAL * self._wave_factor
        # When few remain, accelerate sharply (harder endgame)
        if alive_count <= 1:
            return MIN_STEP_INTERVAL
        if alive_count <= 3:
            return max(MIN_STEP_INTERVAL, base * 0.08)
        if alive_count <= 8:
            return max(MIN_STEP_INTERVAL, base * 0.18)
        if alive_count <= 15:
            return max(MIN_STEP_INTERVAL, base * 0.30)
        return max(MIN_STEP_INTERVAL, base * (0.28 + 0.72 * ratio))

    def alien_fire_interval(self) -> float:
        interval = BASE_ALIEN_FIRE_INTERVAL * self._fire_factor
        return max(MIN_ALIEN_FIRE_INTERVAL, interval)

    def ufo_speed(self) -> float:
        return UFO_SPEED * (1.0 + 0.08 * (self._wave - 1))

    def max_alien_bullets(self) -> int:
        # Wave 1 already allows 2 concurrent shots; caps at 5
        return min(5, 2 + (self._wave - 1) // 1)


def difficulty_for_wave(wave: int) -> DifficultyStrategy:
    return WaveDifficulty(wave)
