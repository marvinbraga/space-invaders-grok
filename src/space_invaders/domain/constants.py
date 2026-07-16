"""Classic Space Invaders layout and scoring constants."""

from typing import Final

# Playfield (logical units — adapters scale to pixels)
PLAYFIELD_WIDTH: Final[int] = 224
PLAYFIELD_HEIGHT: Final[int] = 256

# Formation
FORMATION_ROWS: Final[int] = 5
FORMATION_COLS: Final[int] = 11
ALIEN_WIDTH: Final[int] = 12
ALIEN_HEIGHT: Final[int] = 8
ALIEN_H_GAP: Final[int] = 4
ALIEN_V_GAP: Final[int] = 8
FORMATION_ORIGIN_X: Final[int] = 20
FORMATION_ORIGIN_Y: Final[int] = 40

# Scores by row index (0 = top)
ROW_SCORES: Final[tuple[int, ...]] = (30, 20, 20, 10, 10)

# Player
PLAYER_WIDTH: Final[int] = 15
PLAYER_HEIGHT: Final[int] = 8
PLAYER_Y: Final[int] = 216
PLAYER_SPEED: Final[float] = 80.0
PLAYER_START_X: Final[float] = float(PLAYFIELD_WIDTH // 2 - PLAYER_WIDTH // 2)
INITIAL_LIVES: Final[int] = 3
EXTRA_LIFE_SCORE: Final[int] = 1500

# Bullets
PLAYER_BULLET_SPEED: Final[float] = 180.0
ALIEN_BULLET_SPEED: Final[float] = 70.0
BULLET_WIDTH: Final[int] = 2
BULLET_HEIGHT: Final[int] = 6

# Bunkers
BUNKER_COUNT: Final[int] = 4
BUNKER_WIDTH: Final[int] = 22
BUNKER_HEIGHT: Final[int] = 16
BUNKER_Y: Final[int] = 180
BUNKER_CELL: Final[int] = 2

# UFO
UFO_WIDTH: Final[int] = 16
UFO_HEIGHT: Final[int] = 7
UFO_Y: Final[int] = 24
UFO_SPEED: Final[float] = 40.0
UFO_SPAWN_MIN: Final[float] = 15.0
UFO_SPAWN_MAX: Final[float] = 30.0
# Classic 8080 ROM score table (15 rotating values)
UFO_ROM_SCORES: Final[tuple[int, ...]] = (
    100,
    50,
    50,
    100,
    150,
    100,
    100,
    50,
    300,
    100,
    100,
    100,
    50,
    150,
    100,
)

# Movement
BASE_STEP_INTERVAL: Final[float] = 0.55
MIN_STEP_INTERVAL: Final[float] = 0.04
DROP_DISTANCE: Final[int] = 8
EDGE_MARGIN: Final[int] = 8
INVASION_Y: Final[int] = PLAYER_Y - 8

# Alien fire
BASE_ALIEN_FIRE_INTERVAL: Final[float] = 1.2
MIN_ALIEN_FIRE_INTERVAL: Final[float] = 0.35
