"""Domain entities — always-valid, behavior-rich."""

from __future__ import annotations

from dataclasses import dataclass, field

from space_invaders.domain.constants import (
    ALIEN_HEIGHT,
    ALIEN_WIDTH,
    BULLET_HEIGHT,
    BULLET_WIDTH,
    BUNKER_CELL,
    BUNKER_HEIGHT,
    BUNKER_WIDTH,
    PLAYER_HEIGHT,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    PLAYFIELD_WIDTH,
    UFO_HEIGHT,
    UFO_WIDTH,
)
from space_invaders.domain.value_objects import AlienType, Direction, Position, Rect


@dataclass
class Alien:
    row: int
    col: int
    alien_type: AlienType
    position: Position
    alive: bool = True
    points: int = 10

    def bounds(self) -> Rect:
        return Rect(self.position.x, self.position.y, ALIEN_WIDTH, ALIEN_HEIGHT)

    def kill(self) -> int:
        if not self.alive:
            return 0
        self.alive = False
        return self.points


@dataclass
class Bullet:
    position: Position
    velocity_y: float
    from_player: bool
    active: bool = True

    def bounds(self) -> Rect:
        return Rect(self.position.x, self.position.y, BULLET_WIDTH, BULLET_HEIGHT)

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.position = self.position.moved(0.0, self.velocity_y * dt)
        if self.position.y < -BULLET_HEIGHT or self.position.y > 300:
            self.active = False

    def deactivate(self) -> None:
        self.active = False


@dataclass
class Player:
    position: Position
    lives: int
    width: int = PLAYER_WIDTH
    height: int = PLAYER_HEIGHT
    speed: float = PLAYER_SPEED
    invulnerable: bool = False
    invuln_timer: float = 0.0

    def bounds(self) -> Rect:
        return Rect(self.position.x, self.position.y, self.width, self.height)

    def move(self, direction: Direction, dt: float) -> None:
        dx = direction.value * self.speed * dt
        new_x = self.position.x + dx
        max_x = float(PLAYFIELD_WIDTH - self.width)
        new_x = max(0.0, min(max_x, new_x))
        self.position = Position(new_x, self.position.y)

    def lose_life(self) -> int:
        if self.lives > 0:
            self.lives -= 1
        return self.lives

    def gain_life(self) -> None:
        self.lives += 1

    def start_invulnerability(self, duration: float = 2.0) -> None:
        self.invulnerable = True
        self.invuln_timer = duration

    def tick_invulnerability(self, dt: float) -> None:
        if not self.invulnerable:
            return
        self.invuln_timer -= dt
        if self.invuln_timer <= 0:
            self.invulnerable = False
            self.invuln_timer = 0.0


@dataclass
class Ufo:
    position: Position
    direction: Direction
    active: bool = True
    score_index: int = 0

    def bounds(self) -> Rect:
        return Rect(self.position.x, self.position.y, UFO_WIDTH, UFO_HEIGHT)

    def update(self, dt: float, speed: float) -> None:
        if not self.active:
            return
        dx = self.direction.value * speed * dt
        self.position = self.position.moved(dx, 0.0)
        if self.position.x < -UFO_WIDTH or self.position.x > PLAYFIELD_WIDTH:
            self.active = False

    def deactivate(self) -> None:
        self.active = False


# Classic bunker silhouette: 1 = solid, 0 = empty
_BUNKER_MASK: tuple[str, ...] = (
    "00111111111111111100",
    "01111111111111111110",
    "11111111111111111111",
    "11111111111111111111",
    "11111111111111111111",
    "11111111111111111111",
    "11111111111111111111",
    "11111111111111111111",
    "11111100000000111111",
    "11111000000000011111",
    "11110000000000001111",
    "11100000000000000111",
)


@dataclass
class Bunker:
    index: int
    origin: Position
    cells: list[list[bool]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.cells:
            self.cells = self._default_cells()

    @staticmethod
    def _default_cells() -> list[list[bool]]:
        rows: list[list[bool]] = []
        for line in _BUNKER_MASK:
            row = [ch == "1" for ch in line]
            # pad / trim to BUNKER_WIDTH // cell conceptually
            while len(row) < BUNKER_WIDTH // BUNKER_CELL:
                row.append(False)
            rows.append(row[: BUNKER_WIDTH // BUNKER_CELL])
        while len(rows) < BUNKER_HEIGHT // BUNKER_CELL:
            rows.append([False] * (BUNKER_WIDTH // BUNKER_CELL))
        return rows[: BUNKER_HEIGHT // BUNKER_CELL]

    def bounds(self) -> Rect:
        return Rect(self.origin.x, self.origin.y, BUNKER_WIDTH, BUNKER_HEIGHT)

    def solid_cells(self) -> list[tuple[int, int]]:
        result: list[tuple[int, int]] = []
        for r, row in enumerate(self.cells):
            for c, solid in enumerate(row):
                if solid:
                    result.append((c, r))
        return result

    def damage_at(self, world_x: float, world_y: float, radius: int = 2) -> bool:
        """Destroy cells near impact. Returns True if any cell was destroyed."""
        local_x = world_x - self.origin.x
        local_y = world_y - self.origin.y
        col = int(local_x // BUNKER_CELL)
        row = int(local_y // BUNKER_CELL)
        hit = False
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if dr * dr + dc * dc > radius * radius:
                    continue
                rr, cc = row + dr, col + dc
                in_bounds = 0 <= rr < len(self.cells) and 0 <= cc < len(self.cells[rr])
                if in_bounds and self.cells[rr][cc]:
                    self.cells[rr][cc] = False
                    hit = True
        return hit

    def collides_rect(self, rect: Rect) -> bool:
        if not self.bounds().intersects(rect):
            return False
        for c, r in self.solid_cells():
            cell = Rect(
                self.origin.x + c * BUNKER_CELL,
                self.origin.y + r * BUNKER_CELL,
                BUNKER_CELL,
                BUNKER_CELL,
            )
            if cell.intersects(rect):
                return True
        return False
