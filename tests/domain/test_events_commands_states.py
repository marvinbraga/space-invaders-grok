"""Events, commands, and state machine."""

from space_invaders.domain.commands import CommandKind, InputCommand
from space_invaders.domain.events import (
    DomainEvent,
    EventPublisher,
    PlayerShot,
    ScoreChanged,
)
from space_invaders.domain.game import GameSession
from space_invaders.domain.states import Phase


class _Collector:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def on_event(self, event: DomainEvent) -> None:
        self.events.append(event)


class TestEventPublisher:
    def test_subscribe_publish_unsubscribe(self) -> None:
        bus = EventPublisher()
        c = _Collector()
        bus.subscribe(c)
        bus.subscribe(c)  # idempotent
        bus.publish(PlayerShot())
        assert len(c.events) == 1
        bus.unsubscribe(c)
        bus.publish(PlayerShot())
        assert len(c.events) == 1
        bus.subscribe(c)
        bus.clear()
        bus.publish(PlayerShot())
        assert len(c.events) == 1


class TestStateMachine:
    def test_menu_to_playing(self) -> None:
        g = GameSession(high_score=100)
        assert g.phase is Phase.MENU
        g.handle(InputCommand(CommandKind.START))
        assert g.phase is Phase.PLAYING
        assert g.wave == 1
        assert g.formation.count_alive() == 55
        assert len(g.bunkers) == 4

    def test_pause_resume(self) -> None:
        g = GameSession()
        g.handle(InputCommand(CommandKind.START))
        g.handle(InputCommand(CommandKind.PAUSE))
        assert g.phase is Phase.PAUSED
        g.update(1.0)  # no-op while paused
        g.handle(InputCommand(CommandKind.RESUME))
        assert g.phase is Phase.PLAYING

    def test_esc_to_menu(self) -> None:
        g = GameSession()
        g.handle(InputCommand(CommandKind.START))
        g.handle(InputCommand(CommandKind.TO_MENU))
        assert g.phase is Phase.MENU

    def test_game_over_restart(self) -> None:
        g = GameSession()
        g.handle(InputCommand(CommandKind.START))
        g.player.lives = 0
        g.transition_to(
            __import__("space_invaders.domain.states", fromlist=["GameOverState"]).GameOverState()
        )
        assert g.phase is Phase.GAME_OVER
        g.handle(InputCommand(CommandKind.RESTART))
        assert g.phase is Phase.PLAYING
        assert g.player.lives == 3

    def test_mute_and_quit_flags(self) -> None:
        g = GameSession()
        g.handle(InputCommand(CommandKind.TOGGLE_MUTE))
        assert g.consume_mute_toggle()
        assert not g.consume_mute_toggle()
        g.handle(InputCommand(CommandKind.QUIT))
        assert g.quit_requested

    def test_settings_menu_and_difficulty_select(self) -> None:
        from space_invaders.domain.strategies import DifficultyLevel

        g = GameSession(difficulty_level=DifficultyLevel.MEDIUM)
        assert g.phase is Phase.MENU
        g.handle(InputCommand(CommandKind.MENU_DOWN))
        g.handle(InputCommand(CommandKind.START))
        assert g.phase is Phase.SETTINGS
        # Move to VERY_HARD (index 3 from MEDIUM at index 1)
        g.handle(InputCommand(CommandKind.MENU_DOWN))
        g.handle(InputCommand(CommandKind.MENU_DOWN))
        g.handle(InputCommand(CommandKind.START))
        assert g.phase is Phase.MENU
        assert g.difficulty_level is DifficultyLevel.VERY_HARD
        assert g.consume_settings_dirty()
        assert not g.consume_settings_dirty()

    def test_settings_esc_returns_menu(self) -> None:
        g = GameSession()
        g.handle(InputCommand(CommandKind.MENU_DOWN))
        g.handle(InputCommand(CommandKind.START))
        assert g.phase is Phase.SETTINGS
        g.handle(InputCommand(CommandKind.TO_MENU))
        assert g.phase is Phase.MENU

    def test_menu_quit_option(self) -> None:
        g = GameSession()
        g.handle(InputCommand(CommandKind.MENU_DOWN))
        g.handle(InputCommand(CommandKind.MENU_DOWN))
        g.handle(InputCommand(CommandKind.START))
        assert g.quit_requested

    def test_playing_movement_and_fire(self) -> None:
        bus = EventPublisher()
        c = _Collector()
        bus.subscribe(c)
        g = GameSession(events=bus, rng=__import__("random").Random(0))
        g.handle(InputCommand(CommandKind.START))
        x0 = g.player.position.x
        g.handle(InputCommand(CommandKind.MOVE_LEFT))
        g.update(0.1)
        assert g.player.position.x < x0
        g.handle(InputCommand(CommandKind.STOP_LEFT))
        g.handle(InputCommand(CommandKind.MOVE_RIGHT))
        g.update(0.1)
        g.handle(InputCommand(CommandKind.STOP_RIGHT))
        g.handle(InputCommand(CommandKind.FIRE))
        assert g.player_bullet is not None
        assert any(isinstance(e, PlayerShot) for e in c.events)
        # second fire blocked
        g.handle(InputCommand(CommandKind.FIRE))
        g.handle(InputCommand(CommandKind.TOGGLE_MUTE))
        assert g.mute_toggled

    def test_menu_fire_starts(self) -> None:
        g = GameSession()
        g.handle(InputCommand(CommandKind.FIRE))
        assert g.phase is Phase.PLAYING

    def test_score_changed_event(self) -> None:
        bus = EventPublisher()
        c = _Collector()
        bus.subscribe(c)
        g = GameSession(events=bus)
        g.handle(InputCommand(CommandKind.START))
        # kill via score path
        alien = g.formation.living()[0]
        g._add_score(alien.points)  # noqa: SLF001
        assert any(isinstance(e, ScoreChanged) for e in c.events)
