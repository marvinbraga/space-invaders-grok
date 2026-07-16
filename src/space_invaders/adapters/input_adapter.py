"""Map pygame events to domain InputCommand values."""

from __future__ import annotations

import pygame

from space_invaders.domain.commands import CommandKind, InputCommand

_NAV_UP = frozenset({pygame.K_UP, pygame.K_w})
_NAV_DOWN = frozenset({pygame.K_DOWN, pygame.K_s})
_MOVE_LEFT = frozenset({pygame.K_LEFT, pygame.K_a})
_MOVE_RIGHT = frozenset({pygame.K_RIGHT, pygame.K_d})


class PygameInputAdapter:
    """Translates keyboard events into domain commands (Command pattern edge)."""

    def poll(self) -> list[InputCommand]:
        commands: list[InputCommand] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                commands.append(InputCommand(CommandKind.QUIT))
            elif event.type == pygame.KEYDOWN:
                commands.extend(self._keydown(event))
            elif event.type == pygame.KEYUP:
                commands.extend(self._keyup(event))
        return commands

    def _keydown(self, event: pygame.event.Event) -> list[InputCommand]:
        key = event.key
        mods = pygame.key.get_mods()
        motion = self._motion_down(key)
        if motion:
            return motion
        action = self._action_down(key, mods)
        return action if action else []

    def _motion_down(self, key: int) -> list[InputCommand]:
        if key in _NAV_UP:
            return [InputCommand(CommandKind.MENU_UP)]
        if key in _NAV_DOWN:
            return [InputCommand(CommandKind.MENU_DOWN)]
        if key in _MOVE_LEFT:
            return [
                InputCommand(CommandKind.MOVE_LEFT),
                InputCommand(CommandKind.MENU_UP),
            ]
        if key in _MOVE_RIGHT:
            return [
                InputCommand(CommandKind.MOVE_RIGHT),
                InputCommand(CommandKind.MENU_DOWN),
            ]
        return []

    def _action_down(self, key: int, mods: int) -> list[InputCommand]:
        if key == pygame.K_SPACE:
            return [InputCommand(CommandKind.FIRE)]
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return [InputCommand(CommandKind.START)]
        if key == pygame.K_p:
            return [InputCommand(CommandKind.PAUSE)]
        if key == pygame.K_m:
            return [InputCommand(CommandKind.TOGGLE_MUTE)]
        if key == pygame.K_ESCAPE:
            return [InputCommand(CommandKind.TO_MENU)]
        if key == pygame.K_r and (mods & pygame.KMOD_CTRL):
            return [InputCommand(CommandKind.RESTART)]
        if key == pygame.K_q and (mods & pygame.KMOD_CTRL):
            return [InputCommand(CommandKind.QUIT)]
        return []

    def _keyup(self, event: pygame.event.Event) -> list[InputCommand]:
        key = event.key
        if key in _MOVE_LEFT:
            return [InputCommand(CommandKind.STOP_LEFT)]
        if key in _MOVE_RIGHT:
            return [InputCommand(CommandKind.STOP_RIGHT)]
        return []
