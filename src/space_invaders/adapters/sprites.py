"""Programmatic colorful pixel sprites (no external image assets)."""

from __future__ import annotations

from typing import Final

import pygame

from space_invaders.domain.constants import (
    ALIEN_HEIGHT,
    ALIEN_WIDTH,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    UFO_HEIGHT,
    UFO_WIDTH,
)
from space_invaders.domain.value_objects import AlienType

SCALE: Final[int] = 3

# Classic-inspired palettes
COLOR_BG: Final[tuple[int, int, int]] = (8, 8, 24)
COLOR_PLAYER: Final[tuple[int, int, int]] = (40, 220, 80)
COLOR_SQUID: Final[tuple[int, int, int]] = (80, 220, 255)
COLOR_CRAB: Final[tuple[int, int, int]] = (255, 90, 200)
COLOR_OCTOPUS: Final[tuple[int, int, int]] = (255, 200, 60)
COLOR_UFO: Final[tuple[int, int, int]] = (255, 60, 60)
COLOR_BUNKER: Final[tuple[int, int, int]] = (50, 200, 90)
COLOR_BULLET_P: Final[tuple[int, int, int]] = (255, 255, 180)
COLOR_BULLET_A: Final[tuple[int, int, int]] = (255, 120, 80)
COLOR_TEXT: Final[tuple[int, int, int]] = (230, 230, 255)
COLOR_HI: Final[tuple[int, int, int]] = (255, 220, 80)
COLOR_DIM: Final[tuple[int, int, int]] = (120, 120, 160)


def _pixel_surface(
    pattern: list[str],
    color: tuple[int, int, int],
    scale: int = SCALE,
) -> pygame.Surface:
    h = len(pattern)
    w = max(len(row) for row in pattern) if pattern else 1
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            if ch in ("#", "1", "X"):
                pygame.draw.rect(surf, color, (x * scale, y * scale, scale, scale))
    return surf


def make_player_sprite() -> pygame.Surface:
    pattern = [
        ".......#.......",
        "......###......",
        "......###......",
        "..#############..",
        ".###############.",
        "#################",
        "#################",
        "##..###.###..##",
    ]
    # normalize width
    pattern = [row.ljust(PLAYER_WIDTH, ".")[:PLAYER_WIDTH] for row in pattern]
    pattern = pattern[:PLAYER_HEIGHT]
    return _pixel_surface(pattern, COLOR_PLAYER)


def make_alien_sprite(alien_type: AlienType, frame: int = 0) -> pygame.Surface:
    if alien_type is AlienType.SQUID:
        color = COLOR_SQUID
        frames = (
            [
                "..##..##..##",
                ".##########.",
                "############",
                "##.##..##.##",
                "############",
                "..##....##..",
                ".##..##..##.",
                "##........##",
            ],
            [
                "..##..##..##",
                ".##########.",
                "############",
                "##.##..##.##",
                "############",
                ".##......##.",
                "##.##..##.##",
                ".##......##.",
            ],
        )
    elif alien_type is AlienType.CRAB:
        color = COLOR_CRAB
        frames = (
            [
                ".##......##.",
                "..##....##..",
                ".##########.",
                "##.##..##.##",
                "############",
                "############",
                "#..##..##..#",
                ".##......##.",
            ],
            [
                ".##......##.",
                "#.##....##.#",
                ".##########.",
                "##.##..##.##",
                "############",
                "############",
                ".##......##.",
                "##........##",
            ],
        )
    else:
        color = COLOR_OCTOPUS
        frames = (
            [
                "...######...",
                ".##########.",
                "############",
                "###..##..###",
                "############",
                "..##....##..",
                ".##..##..##.",
                "##........##",
            ],
            [
                "...######...",
                ".##########.",
                "############",
                "###..##..###",
                "############",
                ".##..##..##.",
                "##...##...##",
                ".##......##.",
            ],
        )
    pattern = frames[frame % 2]
    pattern = [row.ljust(ALIEN_WIDTH, ".")[:ALIEN_WIDTH] for row in pattern]
    pattern = pattern[:ALIEN_HEIGHT]
    return _pixel_surface(pattern, color)


def make_ufo_sprite() -> pygame.Surface:
    pattern = [
        "....######....",
        "..##########..",
        ".############.",
        "##.##.##.##.##",
        "##############",
        ".###.####.###.",
        "..##......##..",
    ]
    pattern = [row.ljust(UFO_WIDTH, ".")[:UFO_WIDTH] for row in pattern]
    pattern = pattern[:UFO_HEIGHT]
    return _pixel_surface(pattern, COLOR_UFO)


class SpriteBank:
    """Caches scaled sprites for the frame loop."""

    def __init__(self) -> None:
        self.player = make_player_sprite()
        self.ufo = make_ufo_sprite()
        self.aliens: dict[tuple[AlienType, int], pygame.Surface] = {}
        for t in AlienType:
            for f in (0, 1):
                self.aliens[(t, f)] = make_alien_sprite(t, f)

    def alien(self, alien_type: AlienType, frame: int) -> pygame.Surface:
        return self.aliens[(alien_type, frame % 2)]
