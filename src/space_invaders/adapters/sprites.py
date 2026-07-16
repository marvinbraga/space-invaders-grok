"""Programmatic colorful pixel sprites driven by visual theme palettes."""

from __future__ import annotations

from dataclasses import dataclass
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
from space_invaders.domain.value_objects import AlienType, ThemeId

SCALE: Final[int] = 3

ColorRGB = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class ThemePalette:
    """Presentation colors for one visual theme."""

    bg: ColorRGB
    player: ColorRGB
    squid: ColorRGB
    crab: ColorRGB
    octopus: ColorRGB
    ufo: ColorRGB
    bunker: ColorRGB
    bullet_p: ColorRGB
    bullet_a: ColorRGB
    text: ColorRGB
    hi: ColorRGB
    dim: ColorRGB


# CLASSIC — dark blue / neon (default, matches original look)
_CLASSIC: Final[ThemePalette] = ThemePalette(
    bg=(8, 8, 24),
    player=(40, 220, 80),
    squid=(80, 220, 255),
    crab=(255, 90, 200),
    octopus=(255, 200, 60),
    ufo=(255, 60, 60),
    bunker=(50, 200, 90),
    bullet_p=(255, 255, 180),
    bullet_a=(255, 120, 80),
    text=(230, 230, 255),
    hi=(255, 220, 80),
    dim=(120, 120, 160),
)

# RETRO — warm CRT green / amber
_RETRO: Final[ThemePalette] = ThemePalette(
    bg=(6, 12, 6),
    player=(80, 220, 60),
    squid=(160, 255, 90),
    crab=(220, 180, 40),
    octopus=(255, 170, 40),
    ufo=(255, 120, 30),
    bunker=(60, 180, 50),
    bullet_p=(230, 255, 160),
    bullet_a=(255, 160, 50),
    text=(180, 255, 140),
    hi=(255, 200, 60),
    dim=(90, 140, 70),
)

# NEON — purple / cyan cyberpunk
_NEON: Final[ThemePalette] = ThemePalette(
    bg=(12, 4, 22),
    player=(0, 255, 200),
    squid=(0, 230, 255),
    crab=(255, 60, 220),
    octopus=(180, 80, 255),
    ufo=(255, 40, 160),
    bunker=(40, 220, 180),
    bullet_p=(220, 255, 255),
    bullet_a=(255, 80, 200),
    text=(210, 190, 255),
    hi=(0, 255, 230),
    dim=(130, 90, 180),
)

# ARCADE — bright primary reds / yellows / blues
_ARCADE: Final[ThemePalette] = ThemePalette(
    bg=(10, 10, 30),
    player=(40, 80, 255),
    squid=(255, 40, 40),
    crab=(255, 220, 30),
    octopus=(40, 180, 255),
    ufo=(255, 80, 20),
    bunker=(30, 200, 80),
    bullet_p=(255, 255, 80),
    bullet_a=(255, 60, 40),
    text=(255, 255, 255),
    hi=(255, 230, 40),
    dim=(140, 140, 200),
)

# MIDNIGHT — deep indigo with cool moonlight accents
_MIDNIGHT: Final[ThemePalette] = ThemePalette(
    bg=(4, 6, 18),
    player=(140, 190, 255),
    squid=(100, 160, 255),
    crab=(170, 120, 255),
    octopus=(200, 210, 255),
    ufo=(255, 140, 180),
    bunker=(90, 140, 200),
    bullet_p=(220, 240, 255),
    bullet_a=(200, 140, 255),
    text=(200, 210, 240),
    hi=(180, 200, 255),
    dim=(90, 100, 140),
)

_THEME_PALETTES: Final[dict[ThemeId, ThemePalette]] = {
    ThemeId.CLASSIC: _CLASSIC,
    ThemeId.RETRO: _RETRO,
    ThemeId.NEON: _NEON,
    ThemeId.ARCADE: _ARCADE,
    ThemeId.MIDNIGHT: _MIDNIGHT,
}

# Module-level aliases for CLASSIC (backward-compatible imports)
COLOR_BG: Final[ColorRGB] = _CLASSIC.bg
COLOR_PLAYER: Final[ColorRGB] = _CLASSIC.player
COLOR_SQUID: Final[ColorRGB] = _CLASSIC.squid
COLOR_CRAB: Final[ColorRGB] = _CLASSIC.crab
COLOR_OCTOPUS: Final[ColorRGB] = _CLASSIC.octopus
COLOR_UFO: Final[ColorRGB] = _CLASSIC.ufo
COLOR_BUNKER: Final[ColorRGB] = _CLASSIC.bunker
COLOR_BULLET_P: Final[ColorRGB] = _CLASSIC.bullet_p
COLOR_BULLET_A: Final[ColorRGB] = _CLASSIC.bullet_a
COLOR_TEXT: Final[ColorRGB] = _CLASSIC.text
COLOR_HI: Final[ColorRGB] = _CLASSIC.hi
COLOR_DIM: Final[ColorRGB] = _CLASSIC.dim


def palette_for(theme_id: ThemeId) -> ThemePalette:
    return _THEME_PALETTES[theme_id]


def _pixel_surface(
    pattern: list[str],
    color: ColorRGB,
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


def make_player_sprite(color: ColorRGB = COLOR_PLAYER) -> pygame.Surface:
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
    pattern = [row.ljust(PLAYER_WIDTH, ".")[:PLAYER_WIDTH] for row in pattern]
    pattern = pattern[:PLAYER_HEIGHT]
    return _pixel_surface(pattern, color)


def make_alien_sprite(
    alien_type: AlienType,
    frame: int = 0,
    palette: ThemePalette | None = None,
) -> pygame.Surface:
    colors = palette if palette is not None else _CLASSIC
    if alien_type is AlienType.SQUID:
        color = colors.squid
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
        color = colors.crab
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
        color = colors.octopus
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


def make_ufo_sprite(color: ColorRGB = COLOR_UFO) -> pygame.Surface:
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
    return _pixel_surface(pattern, color)


class SpriteBank:
    """Caches scaled sprites for the frame loop; rebuilds when theme changes."""

    def __init__(self, theme_id: ThemeId = ThemeId.CLASSIC) -> None:
        self._theme_id = theme_id
        self._palette = palette_for(theme_id)
        self.player: pygame.Surface
        self.ufo: pygame.Surface
        self.aliens: dict[tuple[AlienType, int], pygame.Surface]
        self._rebuild()

    @property
    def palette(self) -> ThemePalette:
        return self._palette

    @property
    def theme_id(self) -> ThemeId:
        return self._theme_id

    def ensure_theme(self, theme_id: ThemeId) -> ThemePalette:
        if theme_id is not self._theme_id:
            self._theme_id = theme_id
            self._palette = palette_for(theme_id)
            self._rebuild()
        return self._palette

    def alien(self, alien_type: AlienType, frame: int) -> pygame.Surface:
        return self.aliens[(alien_type, frame % 2)]

    def _rebuild(self) -> None:
        p = self._palette
        self.player = make_player_sprite(p.player)
        self.ufo = make_ufo_sprite(p.ufo)
        self.aliens = {}
        for t in AlienType:
            for f in (0, 1):
                self.aliens[(t, f)] = make_alien_sprite(t, f, p)
