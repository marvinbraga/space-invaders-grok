"""Pygame renderer — draws session snapshot; no game rules."""

from __future__ import annotations

from typing import Final

import pygame

from space_invaders.adapters.bitmap_font import BitmapFont
from space_invaders.adapters.sprites import SCALE, SpriteBank, ThemePalette
from space_invaders.domain.constants import (
    BUNKER_CELL,
    PLAYFIELD_HEIGHT,
    PLAYFIELD_WIDTH,
)
from space_invaders.domain.game import GameSession
from space_invaders.domain.states import MenuOption, Phase

WINDOW_W: Final[int] = PLAYFIELD_WIDTH * SCALE
WINDOW_H: Final[int] = PLAYFIELD_HEIGHT * SCALE

_MENU_LABELS: Final[dict[MenuOption, str]] = {
    MenuOption.PLAY: "JOGAR",
    MenuOption.SETTINGS: "CONFIGURACOES",
    MenuOption.THEME: "TEMAS",
    MenuOption.QUIT: "SAIR",
}


class PygameRenderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._sprites = SpriteBank()
        # Bitmap font — works without pygame.font / SDL_ttf
        self._font = BitmapFont(pixel_size=2)
        self._font_lg = BitmapFont(pixel_size=3)
        self._font_sm = BitmapFont(pixel_size=1)
        self._march_frame = 0
        self._frame_tick = 0

    def draw(self, session: GameSession, muted: bool) -> None:
        # Live-preview the hovered theme on the TEMAS screen; elsewhere use applied theme.
        if session.phase is Phase.THEME_SETTINGS:
            preview_id = session.theme_options[session.theme_index]
        else:
            preview_id = session.theme_id
        palette = self._sprites.ensure_theme(preview_id)
        self._screen.fill(palette.bg)
        self._frame_tick += 1
        if self._frame_tick % 12 == 0:
            self._march_frame = 1 - self._march_frame

        if session.phase is Phase.MENU:
            self._draw_menu(session, palette)
        elif session.phase is Phase.SETTINGS:
            self._draw_settings(session, palette)
        elif session.phase is Phase.THEME_SETTINGS:
            self._draw_theme_settings(session, palette)
        elif session.phase is Phase.GAME_OVER:
            self._draw_world(session, palette)
            self._draw_hud(session, muted, palette)
            self._draw_game_over(session, palette)
        else:
            self._draw_world(session, palette)
            self._draw_hud(session, muted, palette)
            if session.phase is Phase.PAUSED:
                self._draw_center("PAUSED", "P TO RESUME · ESC MENU", palette)

        pygame.display.flip()

    def _sx(self, x: float) -> int:
        return int(x * SCALE)

    def _sy(self, y: float) -> int:
        return int(y * SCALE)

    def _draw_world(self, session: GameSession, palette: ThemePalette) -> None:
        for bunker in session.bunkers:
            for c, r in bunker.solid_cells():
                rect = pygame.Rect(
                    self._sx(bunker.origin.x + c * BUNKER_CELL),
                    self._sy(bunker.origin.y + r * BUNKER_CELL),
                    BUNKER_CELL * SCALE,
                    BUNKER_CELL * SCALE,
                )
                pygame.draw.rect(self._screen, palette.bunker, rect)

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
                palette.bullet_p,
                (self._sx(b.x), self._sy(b.y), b.width * SCALE, b.height * SCALE),
            )
        for bullet in session.alien_bullets:
            if not bullet.active:
                continue
            b = bullet.bounds()
            pygame.draw.rect(
                self._screen,
                palette.bullet_a,
                (self._sx(b.x), self._sy(b.y), b.width * SCALE, b.height * SCALE),
            )

    def _draw_hud(self, session: GameSession, muted: bool, palette: ThemePalette) -> None:
        score_s = f"SCORE  {session.score:04d}"
        hi_s = f"HI-SCORE  {session.high_score:04d}"
        lives_s = f"LIVES  {session.player.lives}"
        wave_s = f"WAVE  {session.wave}"
        diff_s = session.difficulty_level.label
        theme_s = session.theme_id.short_label
        self._blit_text(score_s, 8, 4, palette.text)
        # Single HI-SCORE, right-aligned, no duplication
        hi_surf = self._font.render(hi_s, palette.hi)
        self._screen.blit(hi_surf, (WINDOW_W - hi_surf.get_width() - 8, 4))
        self._blit_text(lives_s, 8, WINDOW_H - 22, palette.text)
        self._blit_text(wave_s, WINDOW_W // 2 - 70, WINDOW_H - 22, palette.dim)
        self._blit_text(diff_s, WINDOW_W // 2 + 20, WINDOW_H - 22, palette.dim)
        self._blit_text(theme_s, WINDOW_W // 2 + 120, WINDOW_H - 22, palette.dim)
        if muted:
            self._blit_text("MUTE", WINDOW_W - 60, WINDOW_H - 22, palette.hi)

    def _draw_menu(self, session: GameSession, palette: ThemePalette) -> None:
        title = self._font_lg.render("SPACE INVADERS", palette.hi)
        self._screen.blit(title, ((WINDOW_W - title.get_width()) // 2, 48))
        sub = self._font.render("TAITO 1978 CLASSIC", palette.dim)
        self._screen.blit(sub, ((WINDOW_W - sub.get_width()) // 2, 84))

        hi = self._font.render(f"HI-SCORE  {session.high_score:04d}", palette.hi)
        self._screen.blit(hi, ((WINDOW_W - hi.get_width()) // 2, 114))

        meta = self._font_sm.render(
            f"DIFICULDADE  {session.difficulty_level.label}  ·  TEMA  {session.theme_id.label}",
            palette.dim,
        )
        self._screen.blit(meta, ((WINDOW_W - meta.get_width()) // 2, 138))

        y = 168
        for index, option in enumerate(session.menu_options):
            label = _MENU_LABELS[option]
            selected = index == session.menu_index
            prefix = "> " if selected else "  "
            color = palette.hi if selected else palette.text
            self._blit_text(f"{prefix}{label}", WINDOW_W // 2 - 90, y, color)
            y += 26

        hints = [
            "SETAS / W S  NAVEGAR",
            "ENTER/SPACE SELECIONAR",
            "M MUTE · ESC SAIR MENU",
        ]
        y = WINDOW_H - 90
        for line in hints:
            surf = self._font_sm.render(line, palette.dim)
            self._screen.blit(surf, ((WINDOW_W - surf.get_width()) // 2, y))
            y += 16

    def _draw_settings(self, session: GameSession, palette: ThemePalette) -> None:
        title = self._font_lg.render("CONFIGURACOES", palette.hi)
        self._screen.blit(title, ((WINDOW_W - title.get_width()) // 2, 70))
        sub = self._font.render("NIVEL DE DIFICULDADE", palette.dim)
        self._screen.blit(sub, ((WINDOW_W - sub.get_width()) // 2, 110))

        y = 160
        for index, level in enumerate(session.settings_options):
            selected = index == session.settings_index
            active = level is session.difficulty_level
            prefix = "> " if selected else "  "
            mark = " *" if active else ""
            color = palette.hi if selected else palette.text
            line = f"{prefix}{level.label}{mark}"
            self._blit_text(line, WINDOW_W // 2 - 100, y, color)
            y += 28

        tip = self._font_sm.render(
            "ENTER CONFIRMA · ESC VOLTA",
            palette.dim,
        )
        self._screen.blit(tip, ((WINDOW_W - tip.get_width()) // 2, WINDOW_H - 50))

    def _draw_theme_settings(self, session: GameSession, palette: ThemePalette) -> None:
        title = self._font_lg.render("TEMAS", palette.hi)
        self._screen.blit(title, ((WINDOW_W - title.get_width()) // 2, 56))
        sub = self._font.render("PALETA VISUAL", palette.dim)
        self._screen.blit(sub, ((WINDOW_W - sub.get_width()) // 2, 96))

        y = 140
        for index, theme in enumerate(session.theme_options):
            selected = index == session.theme_index
            active = theme is session.theme_id
            prefix = "> " if selected else "  "
            mark = " *" if active else ""
            color = palette.hi if selected else palette.text
            line = f"{prefix}{theme.label}{mark}"
            self._blit_text(line, WINDOW_W // 2 - 100, y, color)
            y += 26

        tip = self._font_sm.render(
            "ENTER CONFIRMA · ESC VOLTA",
            palette.dim,
        )
        self._screen.blit(tip, ((WINDOW_W - tip.get_width()) // 2, WINDOW_H - 50))

    def _draw_game_over(self, session: GameSession, palette: ThemePalette) -> None:
        msg = "GAME OVER"
        extra = f"SCORE {session.score:04d}"
        if session.score >= session.high_score and session.score > 0:
            extra += "  ·  NEW HI-SCORE!"
        self._draw_center(msg, extra + "  ·  ENTER REPLAY · ESC MENU", palette)

    def _draw_center(self, title: str, subtitle: str, palette: ThemePalette) -> None:
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self._screen.blit(overlay, (0, 0))
        t = self._font_lg.render(title, palette.hi)
        s = self._font_sm.render(subtitle, palette.text)
        self._screen.blit(t, ((WINDOW_W - t.get_width()) // 2, WINDOW_H // 2 - 30))
        self._screen.blit(s, ((WINDOW_W - s.get_width()) // 2, WINDOW_H // 2 + 10))

    def _blit_text(
        self,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        surf = self._font.render(text, color)
        self._screen.blit(surf, (x, y))
