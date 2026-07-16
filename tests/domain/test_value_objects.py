"""Tests for domain value objects."""

import pytest

from space_invaders.domain.value_objects import Position, Rect, Score, Size, ThemeId


class TestPosition:
    def test_moved(self) -> None:
        p = Position(1.0, 2.0).moved(3.0, -1.0)
        assert p == Position(4.0, 1.0)

    def test_as_int(self) -> None:
        assert Position(1.7, 2.2).as_int() == (1, 2)


class TestSize:
    def test_rejects_non_positive(self) -> None:
        with pytest.raises(ValueError):
            Size(0, 1)
        with pytest.raises(ValueError):
            Size(1, -1)


class TestRect:
    def test_rejects_bad_size(self) -> None:
        with pytest.raises(ValueError):
            Rect(0, 0, 0, 1)

    def test_edges(self) -> None:
        r = Rect(10, 20, 5, 6)
        assert r.left == 10
        assert r.right == 15
        assert r.top == 20
        assert r.bottom == 26

    def test_intersects(self) -> None:
        a = Rect(0, 0, 10, 10)
        b = Rect(5, 5, 10, 10)
        c = Rect(20, 20, 5, 5)
        assert a.intersects(b)
        assert not a.intersects(c)

    def test_contains_point(self) -> None:
        r = Rect(0, 0, 10, 10)
        assert r.contains_point(0, 0)
        assert r.contains_point(9.9, 9.9)
        assert not r.contains_point(10, 5)


class TestScore:
    def test_rejects_negative(self) -> None:
        with pytest.raises(ValueError):
            Score(-1)

    def test_add(self) -> None:
        s = Score(10).add(20)
        assert int(s) == 30

    def test_add_rejects_negative(self) -> None:
        with pytest.raises(ValueError):
            Score(10).add(-1)


class TestThemeId:
    def test_ordered_has_at_least_four_distinct(self) -> None:
        ordered = ThemeId.ordered()
        assert len(ordered) >= 4
        assert len(set(ordered)) == len(ordered)
        assert ThemeId.CLASSIC in ordered
        assert ThemeId.RETRO in ordered
        assert ThemeId.NEON in ordered
        assert ThemeId.ARCADE in ordered

    def test_from_value_and_fallback(self) -> None:
        assert ThemeId.from_value("neon") is ThemeId.NEON
        assert ThemeId.from_value("classic") is ThemeId.CLASSIC
        assert ThemeId.from_value("nope") is ThemeId.CLASSIC

    def test_labels(self) -> None:
        assert ThemeId.CLASSIC.label
        assert ThemeId.RETRO.short_label
        assert ThemeId.CLASSIC.value == "classic"
