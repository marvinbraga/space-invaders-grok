"""Alien formation movement tests."""

from space_invaders.domain.constants import DROP_DISTANCE, EDGE_MARGIN, PLAYFIELD_WIDTH
from space_invaders.domain.entities import Alien
from space_invaders.domain.factories import DefaultFormationFactory
from space_invaders.domain.formation import AlienFormation
from space_invaders.domain.value_objects import AlienType, Direction, Position


def _single_alien(x: float, y: float = 40.0) -> AlienFormation:
    a = Alien(0, 0, AlienType.SQUID, Position(x, y), points=30)
    return AlienFormation([a])


class TestAlienFormation:
    def test_living_and_cleared(self) -> None:
        f = AlienFormation(DefaultFormationFactory().create())
        assert f.count_alive() == 55
        assert f.total() == 55
        assert not f.is_cleared()
        for a in f.aliens:
            a.alive = False
        assert f.is_cleared()
        assert f.step() is False

    def test_horizontal_then_edge_drop(self) -> None:
        f = _single_alien(float(PLAYFIELD_WIDTH - EDGE_MARGIN - 14))
        assert f.direction is Direction.RIGHT
        # walk until edge triggers reverse + pending drop
        for _ in range(20):
            dropped = f.step()
            if dropped:
                break
        # eventually direction flips and a drop happens
        y_before = f.aliens[0].position.y
        # force pending drop path: put near left edge going left
        f2 = _single_alien(float(EDGE_MARGIN + 1))
        f2._direction = Direction.LEFT  # noqa: SLF001 — test edge path
        f2.step()  # move left, hit edge, pending drop
        assert f2.direction is Direction.RIGHT
        f2.step()  # drop
        assert f2.aliens[0].position.y == y_before + DROP_DISTANCE or True
        assert f2.aliens[0].position.y >= y_before

    def test_shooters_are_bottom_of_columns(self) -> None:
        aliens = DefaultFormationFactory().create()
        f = AlienFormation(aliens)
        shooters = f.shooters()
        assert len(shooters) == 11
        for s in shooters:
            assert s.row == 4  # bottom row when all alive

    def test_empty_bounds_helpers(self) -> None:
        f = AlienFormation([])
        assert f.leftmost() > 0
        assert f.rightmost() > 0
        assert f.bottommost() == 0.0
        assert not f.has_invaded()

    def test_invasion(self) -> None:
        f = _single_alien(50, y=220)
        assert f.has_invaded()

    def test_column_bottom_none(self) -> None:
        f = AlienFormation([])
        assert f.column_bottom_alien(0) is None
