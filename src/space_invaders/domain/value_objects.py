"""Immutable value objects for the Space Invaders domain."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Final


class AlienType(Enum):
    """Alien rank by formation row (top = highest score)."""

    SQUID = auto()  # top row, 30 pts
    CRAB = auto()  # middle rows, 20 pts
    OCTOPUS = auto()  # bottom rows, 10 pts


class Direction(Enum):
    LEFT = -1
    RIGHT = 1


@dataclass(frozen=True, slots=True)
class Position:
    x: float
    y: float

    def moved(self, dx: float, dy: float) -> Position:
        return Position(self.x + dx, self.y + dy)

    def as_int(self) -> tuple[int, int]:
        return (int(self.x), int(self.y))


@dataclass(frozen=True, slots=True)
class Size:
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            msg = f"Size must be positive, got {self.width}x{self.height}"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class Rect:
    """Axis-aligned bounding box."""

    x: float
    y: float
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            msg = f"Rect size must be positive, got {self.width}x{self.height}"
            raise ValueError(msg)

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def intersects(self, other: Rect) -> bool:
        return (
            self.left < other.right
            and self.right > other.left
            and self.top < other.bottom
            and self.bottom > other.top
        )

    def contains_point(self, px: float, py: float) -> bool:
        return self.left <= px < self.right and self.top <= py < self.bottom


@dataclass(frozen=True, slots=True)
class Score:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            msg = f"Score cannot be negative: {self.value}"
            raise ValueError(msg)

    def add(self, points: int) -> Score:
        if points < 0:
            msg = f"Cannot add negative points: {points}"
            raise ValueError(msg)
        return Score(self.value + points)

    def __int__(self) -> int:
        return self.value


MAX_HI_SCORE: Final[int] = 999_999
