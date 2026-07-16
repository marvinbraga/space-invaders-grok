"""Factories for formations, bunkers, and bullets (Factory pattern)."""

from __future__ import annotations

from typing import Protocol

from space_invaders.domain.constants import (
    ALIEN_BULLET_SPEED,
    ALIEN_H_GAP,
    ALIEN_HEIGHT,
    ALIEN_V_GAP,
    ALIEN_WIDTH,
    BUNKER_COUNT,
    BUNKER_WIDTH,
    BUNKER_Y,
    FORMATION_COLS,
    FORMATION_ORIGIN_X,
    FORMATION_ORIGIN_Y,
    FORMATION_ROWS,
    PLAYER_BULLET_SPEED,
    PLAYFIELD_WIDTH,
    ROW_SCORES,
)
from space_invaders.domain.entities import Alien, Bullet, Bunker, Player
from space_invaders.domain.value_objects import AlienType, Position


def alien_type_for_row(row: int) -> AlienType:
    if row == 0:
        return AlienType.SQUID
    if row in (1, 2):
        return AlienType.CRAB
    return AlienType.OCTOPUS


class FormationFactory(Protocol):
    def create(self) -> list[Alien]: ...


class BunkerFactory(Protocol):
    def create(self) -> list[Bunker]: ...


class BulletFactory(Protocol):
    def player_bullet(self, player: Player) -> Bullet: ...

    def alien_bullet(self, alien: Alien) -> Bullet: ...


class DefaultFormationFactory:
    """Builds the classic 5×11 alien grid."""

    def create(self) -> list[Alien]:
        aliens: list[Alien] = []
        for row in range(FORMATION_ROWS):
            for col in range(FORMATION_COLS):
                x = FORMATION_ORIGIN_X + col * (ALIEN_WIDTH + ALIEN_H_GAP)
                y = FORMATION_ORIGIN_Y + row * (ALIEN_HEIGHT + ALIEN_V_GAP)
                aliens.append(
                    Alien(
                        row=row,
                        col=col,
                        alien_type=alien_type_for_row(row),
                        position=Position(float(x), float(y)),
                        points=ROW_SCORES[row],
                    )
                )
        return aliens


class DefaultBunkerFactory:
    """Places four destructible bunkers across the playfield."""

    def create(self) -> list[Bunker]:
        bunkers: list[Bunker] = []
        spacing = PLAYFIELD_WIDTH // (BUNKER_COUNT + 1)
        for i in range(BUNKER_COUNT):
            cx = spacing * (i + 1) - BUNKER_WIDTH // 2
            bunkers.append(Bunker(index=i, origin=Position(float(cx), float(BUNKER_Y))))
        return bunkers


class DefaultBulletFactory:
    def player_bullet(self, player: Player) -> Bullet:
        bx = player.position.x + player.width / 2 - 1
        by = player.position.y - 4
        return Bullet(
            position=Position(bx, by),
            velocity_y=-PLAYER_BULLET_SPEED,
            from_player=True,
        )

    def alien_bullet(self, alien: Alien) -> Bullet:
        bx = alien.position.x + ALIEN_WIDTH / 2 - 1
        by = alien.position.y + ALIEN_HEIGHT
        return Bullet(
            position=Position(bx, by),
            velocity_y=ALIEN_BULLET_SPEED,
            from_player=False,
        )
