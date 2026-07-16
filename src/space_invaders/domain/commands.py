"""Input commands (Command pattern)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol


class CommandKind(Enum):
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    STOP_LEFT = auto()
    STOP_RIGHT = auto()
    FIRE = auto()
    START = auto()
    PAUSE = auto()
    RESUME = auto()
    RESTART = auto()
    TO_MENU = auto()
    TOGGLE_MUTE = auto()
    QUIT = auto()


@dataclass(frozen=True, slots=True)
class InputCommand:
    kind: CommandKind


class CommandHandler(Protocol):
    def handle(self, command: InputCommand) -> None: ...
