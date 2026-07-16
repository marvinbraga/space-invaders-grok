"""Tests for domain entities."""

from space_invaders.domain.entities import Alien, Bullet, Bunker, Player, Ufo
from space_invaders.domain.value_objects import AlienType, Direction, Position, Rect


class TestAlien:
    def test_kill_returns_points_once(self) -> None:
        a = Alien(0, 0, AlienType.SQUID, Position(0, 0), points=30)
        assert a.kill() == 30
        assert not a.alive
        assert a.kill() == 0

    def test_bounds(self) -> None:
        a = Alien(0, 0, AlienType.CRAB, Position(5, 7), points=20)
        b = a.bounds()
        assert b.x == 5 and b.y == 7


class TestBullet:
    def test_update_and_deactivate_offscreen(self) -> None:
        b = Bullet(Position(10, 10), velocity_y=-500, from_player=True)
        b.update(1.0)
        assert not b.active

    def test_inactive_does_not_move(self) -> None:
        b = Bullet(Position(10, 10), velocity_y=-10, from_player=True)
        b.deactivate()
        b.update(1.0)
        assert b.position == Position(10, 10)

    def test_downward_offscreen(self) -> None:
        b = Bullet(Position(10, 10), velocity_y=500, from_player=False)
        b.update(1.0)
        assert not b.active


class TestPlayer:
    def test_move_clamps_to_field(self) -> None:
        p = Player(Position(0, 200), lives=3)
        p.move(Direction.LEFT, 1.0)
        assert p.position.x == 0.0
        p.move(Direction.RIGHT, 100.0)
        assert p.position.x > 0

    def test_lives(self) -> None:
        p = Player(Position(0, 0), lives=2)
        assert p.lose_life() == 1
        assert p.lose_life() == 0
        assert p.lose_life() == 0
        p.gain_life()
        assert p.lives == 1

    def test_invulnerability(self) -> None:
        p = Player(Position(0, 0), lives=3)
        p.start_invulnerability(1.0)
        assert p.invulnerable
        p.tick_invulnerability(0.5)
        assert p.invulnerable
        p.tick_invulnerability(0.6)
        assert not p.invulnerable


class TestUfo:
    def test_flies_off_screen(self) -> None:
        u = Ufo(Position(300, 20), Direction.RIGHT)
        u.update(1.0, 100.0)
        assert not u.active

    def test_deactivate(self) -> None:
        u = Ufo(Position(50, 20), Direction.LEFT)
        u.deactivate()
        u.update(0.1, 40.0)
        assert u.position.x == 50


class TestBunker:
    def test_default_has_solid_cells(self) -> None:
        bunker = Bunker(0, Position(10, 180))
        assert len(bunker.solid_cells()) > 0

    def test_damage_destroys_cells(self) -> None:
        bunker = Bunker(0, Position(0, 0))
        before = len(bunker.solid_cells())
        # hit center-ish solid area
        hit = bunker.damage_at(11, 4, radius=3)
        assert hit
        assert len(bunker.solid_cells()) < before

    def test_collides_rect(self) -> None:
        bunker = Bunker(0, Position(0, 0))
        solid = bunker.solid_cells()[0]
        cell_x = solid[0] * 2
        cell_y = solid[1] * 2
        r = Rect(float(cell_x), float(cell_y), 2, 2)
        assert bunker.collides_rect(r)
        far = Rect(200, 200, 2, 2)
        assert not bunker.collides_rect(far)
