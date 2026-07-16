"""Pygame renderer — draws session snapshot; no game rules."""

from __future__ import annotations

from typing import Final

import pygame

from space_invaders.adapters.sprites import (
    COLOR_BG,
    COLOR_BULLET_A,
    COLOR_BULLET_P,
    COLOR_BUNKER,
    COLOR_DIM,
    COLOR_HI,
    COLOR_TEXT,
    SCALE,
    SpriteBank,
)
from space_invaders.domain.constants import (
    BUNKER_CELL,
    PLAYFIELD_HEIGHT,
    PLAYFIELD_WIDTH,
)
from space_invaders.domain.game import GameSession
from space_invaders.domain.states import Phase

WINDOW_W: Final[int] = PLAYFIELD_WIDTH * SCALE
WINDOW_H: Final[int] = PLAYFIELD_HEIGHT * SCALE


class PygameRenderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._sprites = SpriteBank()
        self._font = pygame.font.SysFont("monospace", 18, bold=True)
        self._font_lg = pygame.font.SysFont("monospace", 28, bold=True)
        self._font_sm = pygame.font.SysFont("monospace", 14)
        self._march_frame = 0
        self._frame_tick = 0

    def draw(self, session: GameSession, muted: bool) -> None:
        self._screen.fill(COLOR_BG)
        self._frame_tick += 1
        if self._frame_tick % 12 == 0:
            self._march_frame = 1 - self._march_frame

        if session.phase is Phase.MENU:
            self._draw_menu(session)
        elif session.phase is Phase.GAME_OVER:
            self._draw_world(session)
            self._draw_hud(session, muted)
            self._draw_game_over(session)
        else:
            self._draw_world(session)
            self._draw_hud(session, muted)
            if session.phase is Phase.PAUSED:
                self._draw_center("PAUSED", "P to resume · ESC menu")

        pygame.display.flip()

    def _sx(self, x: float) -> int:
        return int(x * SCALE)

    def _sy(self, y: float) -> int:
        return int(y * SCALE)

    def _draw_world(self, session: GameSession) -> None:
        for bunker in session.bunkers:
            for c, r in bunker.solid_cells():
                rect = pygame.Rect(
                    self._sx(bunker.origin.x + c * BUNKER_CELL),
                    self._sy(bunker.origin.y + r * BUNKER_CELL),
                    BUNKER_CELL * SCALE,
                    BUNKER_CELL * SCALE,
                )
                pygame.draw.rect(self._screen, COLOR_BUNKER, rect)

        for alien in session.formation.living():
            spr = self._sprites.alien(alien.alien_type, self._march_frame)
            self._screen.blit(spr, (self._sx(alien.position.x), self._sy(alien.position.y)))

        if session.ufo is not None and session.ufo.active:
            self._screen.blit(
                self._sprites.ufo,
                (self._sx(session.ufo.position.x), self._sy(session.ufo.position.y)),
            )

        player = session.player
        if not player.invulnerable or (self._frame_tick // 4) % 2 == 0:
            self._screen.blit(
                self._sprites.player,
                (self._sx(player.position.x), self._sy(player.position.y)),
            )

        if session.player_bullet is not None and session.player_bullet.active:
            b = session.player_bullet.bounds()
            pygame.draw.rect(
                self._screen,
                COLOR_BULLET_P,
                (self._sx(b.x), self._sy(b.y), b.width * SCALE, b.height * SCALE),
            )
        for bullet in session.alien_bullets:
            if not bullet.active:
                continue
            b = bullet.bounds()
            pygame.draw.rect(
                self._screen,
                COLOR_BULLET_A,
                (self._sx(b.x), self._sy(b.y), b.width * SCALE, b.height * SCALE),
            )

    def _draw_hud(self, session: GameSession, muted: bool) -> None:
        score_s = f"SCORE  {session.score:04d}"
        hi_s = f"HI-SCORE  {session.high_score:04d}"
        lives_s = f"LIVES  {session.player.lives}"
        wave_s = f"WAVE  {session.wave}"
        self._blit_text(score_s, 8, 4, COLOR_TEXT)
        # Single HI-SCORE, right-aligned, no duplication
        hi_surf = self._font.render(hi_s, True, COLOR_HI)
        self._screen.blit(hi_surf, (WINDOW_W - hi_surf.get_width() - 8, 4))
        self._blit_text(lives_s, 8, WINDOW_H - 22, COLOR_TEXT)
        self._blit_text(wave_s, WINDOW_W // 2 - 40, WINDOW_H - 22, COLOR_DIM)
        if muted:
            self._blit_text("MUTE", WINDOW_W - 60, WINDOW_H - 22, COLOR_HI)

    def _draw_menu(self, session: GameSession) -> None:
        title = self._font_lg.render("SPACE INVADERS", True, COLOR_HI)
        self._screen.blit(title, ((WINDOW_W - title.get_width()) // 2, 70))
        sub = self._font.render("TAITO 1978 CLASSIC", True, COLOR_DIM)
        self._screen.blit(sub, ((WINDOW_W - sub.get_width()) // 2, 110))

        hi = self._font.render(f"HI-SCORE  {session.high_score:04d}", True, COLOR_HI)
        self._screen.blit(hi, ((WINDOW_W - hi.get_width()) // 2, 150))

        lines = [
            "ENTER / SPACE  Start",
            "← →  or  A D   Move",
            "SPACE          Fire",
            "P              Pause",
            "Ctrl+R         Restart",
            "M              Mute",
            "ESC            Menu",
        ]
        y = 190
        for line in lines:
            self._blit_text(line, WINDOW_W // 2 - 120, y, COLOR_TEXT)
            y += 22

        tip = self._font_sm.render("Destroy the formation. Don't let them land.", True, COLOR_DIM)
        self._screen.blit(tip, ((WINDOW_W - tip.get_width()) // 2, WINDOW_H - 40))

    def _draw_game_over(self, session: GameSession) -> None:
        msg = "GAME OVER"
        extra = f"SCORE {session.score:04d}"
        if session.score >= session.high_score and session.score > 0:
            extra += "  ·  NEW HI-SCORE!"
        self._draw_center(msg, extra + "  ·  ENTER replay · ESC menu")

    def _draw_center(self, title: str, subtitle: str) -> None:
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self._screen.blit(overlay, (0, 0))
        t = self._font_lg.render(title, True, COLOR_HI)
        s = self._font_sm.render(subtitle, True, COLOR_TEXT)
        self._screen.blit(t, ((WINDOW_W - t.get_width()) // 2, WINDOW_H // 2 - 30))
        self._screen.blit(s, ((WINDOW_W - s.get_width()) // 2, WINDOW_H // 2 + 10))

    def _blit_text(
        self,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        surf = self._font.render(text, True, color)
        self._screen.blit(surf, (x, y))
