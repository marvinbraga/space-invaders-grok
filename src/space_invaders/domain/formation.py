"""Alien formation movement: group step, edge reverse + drop."""

from __future__ import annotations

from space_invaders.domain.constants import (
    ALIEN_HEIGHT,
    ALIEN_WIDTH,
    DROP_DISTANCE,
    EDGE_MARGIN,
    FORMATION_STEP_PIXELS,
    INVASION_Y,
    PLAYFIELD_WIDTH,
)
from space_invaders.domain.entities import Alien
from space_invaders.domain.value_objects import Direction, Position


class AlienFormation:
    """Manages the living alien grid as a cohesive group."""

    def __init__(self, aliens: list[Alien]) -> None:
        self._aliens = aliens
        self._direction = Direction.RIGHT
        self._step_pixels = FORMATION_STEP_PIXELS
        self._pending_drop = False

    @property
    def aliens(self) -> list[Alien]:
        return self._aliens

    @property
    def direction(self) -> Direction:
        return self._direction

    def living(self) -> list[Alien]:
        return [a for a in self._aliens if a.alive]

    def count_alive(self) -> int:
        return sum(1 for a in self._aliens if a.alive)

    def total(self) -> int:
        return len(self._aliens)

    def is_cleared(self) -> bool:
        return self.count_alive() == 0

    def leftmost(self) -> float:
        living = self.living()
        if not living:
            return float(EDGE_MARGIN)
        return min(a.position.x for a in living)

    def rightmost(self) -> float:
        living = self.living()
        if not living:
            return float(PLAYFIELD_WIDTH - EDGE_MARGIN)
        return max(a.position.x + ALIEN_WIDTH for a in living)

    def bottommost(self) -> float:
        living = self.living()
        if not living:
            return 0.0
        return max(a.position.y + ALIEN_HEIGHT for a in living)

    def has_invaded(self) -> bool:
        return self.bottommost() >= INVASION_Y

    def step(self) -> bool:
        """
        Advance one march step. Returns True if a drop occurred.
        """
        if self.is_cleared():
            return False
        if self._pending_drop:
            self._drop()
            self._pending_drop = False
            return True
        self._move_horizontal()
        if self._hits_edge():
            self._direction = (
                Direction.LEFT if self._direction is Direction.RIGHT else Direction.RIGHT
            )
            self._pending_drop = True
        return False

    def _move_horizontal(self) -> None:
        dx = self._direction.value * self._step_pixels
        for alien in self.living():
            alien.position = alien.position.moved(dx, 0.0)

    def _drop(self) -> None:
        for alien in self.living():
            alien.position = Position(alien.position.x, alien.position.y + DROP_DISTANCE)

    def _hits_edge(self) -> bool:
        if self._direction is Direction.RIGHT:
            return self.rightmost() >= PLAYFIELD_WIDTH - EDGE_MARGIN
        return self.leftmost() <= EDGE_MARGIN

    def column_bottom_alien(self, col: int) -> Alien | None:
        candidates = [a for a in self.living() if a.col == col]
        if not candidates:
            return None
        return max(candidates, key=lambda a: a.position.y)

    def shooters(self) -> list[Alien]:
        """Bottom-most alive alien in each occupied column may fire."""
        cols = {a.col for a in self.living()}
        result: list[Alien] = []
        for col in sorted(cols):
            shooter = self.column_bottom_alien(col)
            if shooter is not None:
                result.append(shooter)
        return result
