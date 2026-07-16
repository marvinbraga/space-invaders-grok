"""Composition root — wires ports to adapters; not a Facade class."""

from __future__ import annotations

import sys
from pathlib import Path

import pygame

from space_invaders.adapters.audio import NullAudio, PygameAudioAdapter
from space_invaders.adapters.input_adapter import PygameInputAdapter
from space_invaders.adapters.renderer import WINDOW_H, WINDOW_W, PygameRenderer
from space_invaders.adapters.score_repository import FileScoreRepository
from space_invaders.adapters.settings_repository import FileSettingsRepository
from space_invaders.application.audio_events import AudioEventBridge
from space_invaders.application.high_score import HighScoreService
from space_invaders.application.settings import SettingsService
from space_invaders.domain.game import GameSession
from space_invaders.domain.states import Phase

_FPS = 60
_DATA_DIR = Path.home() / ".local" / "share" / "space-invaders-grok"
_HIGH_SCORE_PATH = _DATA_DIR / "highscore.json"
_SETTINGS_PATH = _DATA_DIR / "settings.json"
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
_SOUNDS_DIR = _PACKAGE_ROOT / "assets" / "sounds"


def _resolve_sounds_dir() -> Path:
    candidates = [
        _SOUNDS_DIR,
        Path.cwd() / "assets" / "sounds",
        Path(__file__).resolve().parent.parent.parent.parent / "assets" / "sounds",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    return _SOUNDS_DIR


def _build_audio(sounds_dir: Path) -> PygameAudioAdapter | NullAudio:
    try:
        return PygameAudioAdapter(sounds_dir)
    except Exception:  # noqa: BLE001 — fall back silently for headless
        return NullAudio()


def run() -> int:
    pygame.init()
    pygame.display.set_caption("Space Invaders")
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

    score_repo = FileScoreRepository(_HIGH_SCORE_PATH)
    high_scores = HighScoreService(score_repo)
    hi = high_scores.load()

    settings = SettingsService(FileSettingsRepository(_SETTINGS_PATH))
    difficulty = settings.load_difficulty()
    theme = settings.load_theme()

    audio = _build_audio(_resolve_sounds_dir())
    session = GameSession(high_score=hi, difficulty_level=difficulty, theme_id=theme)
    audio_bridge = AudioEventBridge(audio)
    session.events.subscribe(audio_bridge)

    renderer = PygameRenderer(screen)
    inputs = PygameInputAdapter()

    running = True
    while running:
        dt_ms = clock.tick(_FPS)
        dt = dt_ms / 1000.0

        for command in inputs.poll():
            session.handle(command)

        if session.consume_mute_toggle():
            audio.toggle_mute()

        if session.consume_settings_dirty():
            settings.save_difficulty(session.difficulty_level)

        if session.consume_theme_dirty():
            settings.save_theme(session.theme_id)

        session.update(dt)

        if session.phase in (
            Phase.MENU,
            Phase.GAME_OVER,
            Phase.SETTINGS,
            Phase.THEME_SETTINGS,
        ):
            new_hi = high_scores.save_if_higher(session.score, session.high_score)
            session.sync_high_score(new_hi)

        renderer.draw(session, muted=audio.is_muted())

        if session.quit_requested:
            high_scores.save_if_higher(session.score, session.high_score)
            settings.save_difficulty(session.difficulty_level)
            settings.save_theme(session.theme_id)
            running = False

    pygame.quit()
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
