"""Game flow states (State pattern)."""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Protocol

from space_invaders.domain.commands import CommandKind, InputCommand

if TYPE_CHECKING:
    from space_invaders.domain.game import GameSession


class Phase(Enum):
    MENU = auto()
    SETTINGS = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class MenuOption(Enum):
    PLAY = 0
    SETTINGS = 1
    QUIT = 2


class GameState(Protocol):
    phase: Phase

    def enter(self, session: GameSession) -> None: ...

    def handle(self, session: GameSession, command: InputCommand) -> None: ...

    def update(self, session: GameSession, dt: float) -> None: ...


class MenuState:
    phase: Phase = Phase.MENU

    def enter(self, session: GameSession) -> None:
        session.reset_menu_cursor()

    def handle(self, session: GameSession, command: InputCommand) -> None:
        kind = command.kind
        if kind == CommandKind.MENU_UP:
            session.menu_cursor_up()
        elif kind == CommandKind.MENU_DOWN:
            session.menu_cursor_down()
        elif kind in (CommandKind.START, CommandKind.FIRE):
            session.activate_menu_selection()
        elif kind == CommandKind.QUIT:
            session.request_quit()
        elif kind == CommandKind.TOGGLE_MUTE:
            session.toggle_mute_flag()

    def update(self, session: GameSession, dt: float) -> None:
        del session, dt


class SettingsState:
    phase: Phase = Phase.SETTINGS

    def enter(self, session: GameSession) -> None:
        session.sync_settings_cursor()

    def handle(self, session: GameSession, command: InputCommand) -> None:
        kind = command.kind
        if kind == CommandKind.MENU_UP:
            session.settings_cursor_up()
        elif kind == CommandKind.MENU_DOWN:
            session.settings_cursor_down()
        elif kind in (CommandKind.START, CommandKind.FIRE):
            session.apply_settings_selection()
        elif kind == CommandKind.TO_MENU:
            session.transition_to(MenuState())
        elif kind == CommandKind.QUIT:
            session.request_quit()
        elif kind == CommandKind.TOGGLE_MUTE:
            session.toggle_mute_flag()

    def update(self, session: GameSession, dt: float) -> None:
        del session, dt


class PlayingState:
    phase: Phase = Phase.PLAYING

    def enter(self, session: GameSession) -> None:
        del session

    def handle(self, session: GameSession, command: InputCommand) -> None:
        kind = command.kind
        if self._handle_motion(session, kind):
            return
        self._handle_action(session, kind)

    def _handle_motion(self, session: GameSession, kind: CommandKind) -> bool:
        if kind == CommandKind.MOVE_LEFT:
            session.set_moving_left(True)
            return True
        if kind == CommandKind.MOVE_RIGHT:
            session.set_moving_right(True)
            return True
        if kind == CommandKind.STOP_LEFT:
            session.set_moving_left(False)
            return True
        if kind == CommandKind.STOP_RIGHT:
            session.set_moving_right(False)
            return True
        return False

    def _handle_action(self, session: GameSession, kind: CommandKind) -> None:
        if kind == CommandKind.FIRE:
            session.try_fire()
        elif kind == CommandKind.PAUSE:
            session.transition_to(PausedState())
        elif kind == CommandKind.TO_MENU:
            session.return_to_menu()
        elif kind == CommandKind.RESTART:
            session.restart()
        elif kind == CommandKind.TOGGLE_MUTE:
            session.toggle_mute_flag()
        elif kind == CommandKind.QUIT:
            session.request_quit()

    def update(self, session: GameSession, dt: float) -> None:
        session.tick_play(dt)


class PausedState:
    phase: Phase = Phase.PAUSED

    def enter(self, session: GameSession) -> None:
        session.set_moving_left(False)
        session.set_moving_right(False)

    def handle(self, session: GameSession, command: InputCommand) -> None:
        kind = command.kind
        if kind in (CommandKind.PAUSE, CommandKind.RESUME, CommandKind.START):
            session.transition_to(PlayingState())
        elif kind == CommandKind.TO_MENU:
            session.return_to_menu()
        elif kind == CommandKind.RESTART:
            session.restart()
        elif kind == CommandKind.TOGGLE_MUTE:
            session.toggle_mute_flag()
        elif kind == CommandKind.QUIT:
            session.request_quit()

    def update(self, session: GameSession, dt: float) -> None:
        del session, dt


class GameOverState:
    phase: Phase = Phase.GAME_OVER

    def enter(self, session: GameSession) -> None:
        session.set_moving_left(False)
        session.set_moving_right(False)
        session.finalize_game_over()

    def handle(self, session: GameSession, command: InputCommand) -> None:
        kind = command.kind
        if kind in (CommandKind.START, CommandKind.FIRE, CommandKind.RESTART):
            session.restart()
        elif kind == CommandKind.TO_MENU:
            session.return_to_menu()
        elif kind == CommandKind.TOGGLE_MUTE:
            session.toggle_mute_flag()
        elif kind == CommandKind.QUIT:
            session.request_quit()

    def update(self, session: GameSession, dt: float) -> None:
        del session, dt


__all__ = [
    "GameOverState",
    "GameState",
    "MenuOption",
    "MenuState",
    "PausedState",
    "Phase",
    "PlayingState",
    "SettingsState",
]
