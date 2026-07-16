"""Integration-style domain tests for GameSession rules."""

from __future__ import annotations

import random

import pytest

from space_invaders.domain.commands import CommandKind, InputCommand
from space_invaders.domain.constants import (
    EXTRA_LIFE_SCORE,
    INVASION_Y,
    UFO_ROM_SCORES,
)
from space_invaders.domain.entities import Bullet, Ufo
from space_invaders.domain.events import (
    AlienHit,
    DomainEvent,
    EventPublisher,
    ExtraLifeAwarded,
    GameOverEvent,
    PlayerHit,
    UfoHit,
    WaveCleared,
    WaveStarted,
)
from space_invaders.domain.game import ClassicWaveSetup, GameSession
from space_invaders.domain.states import GameOverState, Phase, PlayingState
from space_invaders.domain.value_objects import Direction, Position


class _Collector:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def on_event(self, event: DomainEvent) -> None:
        self.events.append(event)


def _started(seed: int = 0, high: int = 0) -> tuple[GameSession, _Collector]:
    bus = EventPublisher()
    c = _Collector()
    bus.subscribe(c)
    g = GameSession(events=bus, rng=random.Random(seed), high_score=high)
    g.handle(InputCommand(CommandKind.START))
    return g, c


class TestGameRules:
    def test_negative_dt_rejected(self) -> None:
        g, _ = _started()
        with pytest.raises(ValueError):
            g.update(-0.1)

    def test_one_player_bullet(self) -> None:
        g, _ = _started()
        g.handle(InputCommand(CommandKind.FIRE))
        first = g.player_bullet
        g.handle(InputCommand(CommandKind.FIRE))
        assert g.player_bullet is first

    def test_bullet_hits_alien(self) -> None:
        g, c = _started()
        target = g.formation.living()[0]
        g._player_bullet = Bullet(  # noqa: SLF001
            position=Position(target.position.x + 2, target.position.y + 2),
            velocity_y=0,
            from_player=True,
        )
        g._resolve_collisions()  # noqa: SLF001
        assert not target.alive
        assert g.score == target.points
        assert any(isinstance(e, AlienHit) for e in c.events)

    def test_bullet_hits_bunker(self) -> None:
        g, _ = _started()
        bunker = g.bunkers[0]
        solids = bunker.solid_cells()
        assert solids
        cx, cy = solids[len(solids) // 2]
        wx = bunker.origin.x + cx * 2 + 1
        wy = bunker.origin.y + cy * 2 + 1
        before = len(bunker.solid_cells())
        g._player_bullet = Bullet(  # noqa: SLF001
            position=Position(wx, wy),
            velocity_y=0,
            from_player=True,
        )
        g._resolve_collisions()  # noqa: SLF001
        assert len(bunker.solid_cells()) < before
        assert g.player_bullet is None

    def test_alien_bullet_hits_player(self) -> None:
        g, c = _started()
        p = g.player
        g._alien_bullets = [  # noqa: SLF001
            Bullet(
                position=Position(p.position.x + 2, p.position.y + 2),
                velocity_y=0,
                from_player=False,
            )
        ]
        lives = p.lives
        g._resolve_collisions()  # noqa: SLF001
        assert g.player.lives == lives - 1
        assert any(isinstance(e, PlayerHit) for e in c.events)
        assert g.player.invulnerable

    def test_player_death_game_over(self) -> None:
        g, c = _started()
        g.player.lives = 1
        p = g.player
        g._alien_bullets = [  # noqa: SLF001
            Bullet(
                position=Position(p.position.x + 2, p.position.y + 2),
                velocity_y=0,
                from_player=False,
            )
        ]
        g._resolve_collisions()  # noqa: SLF001
        assert g.phase is Phase.GAME_OVER
        assert any(isinstance(e, GameOverEvent) for e in c.events)

    def test_extra_life_once_at_1500(self) -> None:
        g, c = _started()
        g._add_score(EXTRA_LIFE_SCORE)  # noqa: SLF001
        assert g.player.lives == 4
        assert any(isinstance(e, ExtraLifeAwarded) for e in c.events)
        g._add_score(EXTRA_LIFE_SCORE)  # noqa: SLF001
        assert g.player.lives == 4  # only once

    def test_wave_clear_rebuilds_bunkers(self) -> None:
        g, c = _started()
        # damage a bunker then clear wave
        bunker = g.bunkers[0]
        bunker.damage_at(bunker.origin.x + 10, bunker.origin.y + 4, radius=5)
        damaged = len(bunker.solid_cells())
        for a in g.formation.aliens:
            a.alive = False
        g._check_wave_clear()  # noqa: SLF001
        assert g.wave == 2
        assert any(isinstance(e, WaveCleared) for e in c.events)
        assert any(isinstance(e, WaveStarted) and e.wave == 2 for e in c.events)
        assert len(g.bunkers[0].solid_cells()) > damaged

    def test_invasion_game_over(self) -> None:
        g, _ = _started()
        for a in g.formation.living():
            a.position = Position(a.position.x, float(INVASION_Y))
        g._check_game_over()  # noqa: SLF001
        assert g.phase is Phase.GAME_OVER
        assert g.player.lives == 0

    def test_ufo_hit_rom_scores(self) -> None:
        g, c = _started(seed=1)
        g._ufo = Ufo(  # noqa: SLF001
            position=Position(50, 24),
            direction=Direction.RIGHT,
            score_index=0,
        )
        g._ufo_score_index = 0  # noqa: SLF001
        g._player_bullet = Bullet(  # noqa: SLF001
            position=Position(52, 25),
            velocity_y=0,
            from_player=True,
        )
        g._resolve_collisions()  # noqa: SLF001
        assert g.score == UFO_ROM_SCORES[0]
        assert any(isinstance(e, UfoHit) for e in c.events)

    def test_ufo_spawn_and_despawn(self) -> None:
        g, _ = _started(seed=2)
        # ensure enough aliens alive
        assert g.formation.count_alive() >= 8
        g._ufo_timer = 0.0  # noqa: SLF001
        g._update_ufo(0.01)  # noqa: SLF001
        assert g.ufo is not None
        assert g.ufo.active
        # fly off
        assert g.ufo is not None
        g.ufo.position = Position(400, 24)
        g._update_ufo(0.1)  # noqa: SLF001
        assert g.ufo is None

    def test_march_publishes_event(self) -> None:
        g, c = _started()
        g._step_timer = 10.0  # noqa: SLF001
        g._march_aliens(0.01)  # noqa: SLF001
        from space_invaders.domain.events import AlienMarched

        assert any(isinstance(e, AlienMarched) for e in c.events)

    def test_alien_fire_spawns_bullet(self) -> None:
        g, _ = _started(seed=3)
        g._fire_timer = 100.0  # noqa: SLF001
        g._alien_fire(0.01)  # noqa: SLF001
        assert len(g.alien_bullets) >= 1

    def test_high_score_tracks(self) -> None:
        g, _ = _started(high=50)
        assert g.high_score == 50
        g._add_score(100)  # noqa: SLF001
        assert g.high_score == 100

    def test_return_to_menu_keeps_high(self) -> None:
        g, _ = _started(high=10)
        g._add_score(500)  # noqa: SLF001
        g.handle(InputCommand(CommandKind.TO_MENU))
        assert g.phase is Phase.MENU
        assert g.high_score >= 500

    def test_paused_restart(self) -> None:
        g, _ = _started()
        g.handle(InputCommand(CommandKind.PAUSE))
        g.handle(InputCommand(CommandKind.RESTART))
        assert g.phase is Phase.PLAYING

    def test_game_over_to_menu(self) -> None:
        g, _ = _started()
        g.transition_to(GameOverState())
        g.handle(InputCommand(CommandKind.TO_MENU))
        assert g.phase is Phase.MENU

    def test_classic_wave_setup_hooks(self) -> None:
        setup = ClassicWaveSetup()
        g = GameSession()
        g.handle(InputCommand(CommandKind.START))
        f = setup.build_formation(g)
        assert f.count_alive() == 55
        b = setup.build_bunkers(g)
        assert len(b) == 4

    def test_tick_play_full_frame(self) -> None:
        g, _ = _started(seed=5)
        g.handle(InputCommand(CommandKind.MOVE_RIGHT))
        g.handle(InputCommand(CommandKind.FIRE))
        g.update(0.05)
        assert g.phase is Phase.PLAYING

    def test_finalize_game_over_idempotent(self) -> None:
        g, c = _started()
        g.transition_to(GameOverState())
        n = sum(1 for e in c.events if isinstance(e, GameOverEvent))
        g.finalize_game_over()
        n2 = sum(1 for e in c.events if isinstance(e, GameOverEvent))
        assert n2 == n

    def test_playing_quit(self) -> None:
        g, _ = _started()
        g.handle(InputCommand(CommandKind.QUIT))
        assert g.quit_requested

    def test_alien_bullet_hits_bunker(self) -> None:
        g, _ = _started()
        bunker = g.bunkers[1]
        solids = bunker.solid_cells()
        cx, cy = solids[0]
        wx = bunker.origin.x + cx * 2
        wy = bunker.origin.y + cy * 2
        g._alien_bullets = [  # noqa: SLF001
            Bullet(position=Position(wx, wy), velocity_y=0, from_player=False)
        ]
        before = len(bunker.solid_cells())
        g._resolve_collisions()  # noqa: SLF001
        assert len(bunker.solid_cells()) < before

    def test_invulnerable_player_ignores_bullets(self) -> None:
        g, _ = _started()
        g.player.start_invulnerability(5.0)
        p = g.player
        g._alien_bullets = [  # noqa: SLF001
            Bullet(
                position=Position(p.position.x + 2, p.position.y + 2),
                velocity_y=0,
                from_player=False,
            )
        ]
        lives = p.lives
        g._resolve_collisions()  # noqa: SLF001
        assert g.player.lives == lives

    def test_bullet_expires(self) -> None:
        g, _ = _started()
        g.handle(InputCommand(CommandKind.FIRE))
        for _ in range(50):
            g.update(0.1)
        assert g.player_bullet is None

    def test_ufo_not_when_few_aliens(self) -> None:
        g, _ = _started()
        for i, a in enumerate(g.formation.aliens):
            a.alive = i < 3
        g._ufo_timer = 0.0  # noqa: SLF001
        g._update_ufo(0.01)  # noqa: SLF001
        assert g.ufo is None

    def test_transition_playing_enter(self) -> None:
        g, _ = _started()
        g.transition_to(PlayingState())
        assert g.phase is Phase.PLAYING
