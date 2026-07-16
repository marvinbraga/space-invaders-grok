"""Factories and difficulty strategies."""

import pytest

from space_invaders.domain.constants import (
    FORMATION_COLS,
    FORMATION_ROWS,
    ROW_SCORES,
    UFO_ROM_SCORES,
)
from space_invaders.domain.entities import Player
from space_invaders.domain.factories import (
    DefaultBulletFactory,
    DefaultBunkerFactory,
    DefaultFormationFactory,
    alien_type_for_row,
)
from space_invaders.domain.strategies import WaveDifficulty, difficulty_for_wave
from space_invaders.domain.value_objects import AlienType, Position


class TestFormationFactory:
    def test_5x11_grid_and_scores(self) -> None:
        aliens = DefaultFormationFactory().create()
        assert len(aliens) == FORMATION_ROWS * FORMATION_COLS
        by_row = {r: [] for r in range(FORMATION_ROWS)}
        for a in aliens:
            by_row[a.row].append(a)
            assert a.points == ROW_SCORES[a.row]
        for r in range(FORMATION_ROWS):
            assert len(by_row[r]) == FORMATION_COLS

    def test_alien_types(self) -> None:
        assert alien_type_for_row(0) is AlienType.SQUID
        assert alien_type_for_row(1) is AlienType.CRAB
        assert alien_type_for_row(2) is AlienType.CRAB
        assert alien_type_for_row(3) is AlienType.OCTOPUS
        assert alien_type_for_row(4) is AlienType.OCTOPUS


class TestBunkerFactory:
    def test_four_bunkers(self) -> None:
        bunkers = DefaultBunkerFactory().create()
        assert len(bunkers) == 4
        assert [b.index for b in bunkers] == [0, 1, 2, 3]


class TestBulletFactory:
    def test_player_and_alien_bullets(self) -> None:
        factory = DefaultBulletFactory()
        player = Player(Position(50, 200), lives=3)
        pb = factory.player_bullet(player)
        assert pb.from_player and pb.velocity_y < 0
        aliens = DefaultFormationFactory().create()
        ab = factory.alien_bullet(aliens[0])
        assert not ab.from_player and ab.velocity_y > 0


class TestWaveDifficulty:
    def test_rejects_wave_zero(self) -> None:
        with pytest.raises(ValueError):
            WaveDifficulty(0)

    def test_acceleration_with_fewer_aliens(self) -> None:
        d = difficulty_for_wave(1)
        full = d.step_interval(55, 55)
        few = d.step_interval(2, 55)
        one = d.step_interval(1, 55)
        assert few < full
        assert one <= few

    def test_wave_progresses_difficulty(self) -> None:
        w1 = difficulty_for_wave(1)
        w5 = difficulty_for_wave(5)
        assert w5.step_interval(40, 55) < w1.step_interval(40, 55)
        assert w5.alien_fire_interval() < w1.alien_fire_interval()
        assert w5.ufo_speed() > w1.ufo_speed()
        assert w5.max_alien_bullets() >= w1.max_alien_bullets()

    def test_empty_total_returns_min(self) -> None:
        d = difficulty_for_wave(1)
        assert d.step_interval(0, 0) > 0

    def test_ufo_rom_table_length(self) -> None:
        assert len(UFO_ROM_SCORES) == 15
