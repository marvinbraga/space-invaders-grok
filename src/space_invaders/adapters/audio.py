"""Audio adapter: pygame.mixer with paplay subprocess fallback."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

# Optional pygame — imported lazily so domain tests need no display


class PygameAudioAdapter:
    """Plays named WAV files. Satisfies AudioPort structurally."""

    def __init__(self, sounds_dir: Path) -> None:
        self._sounds_dir = sounds_dir
        self._muted = False
        self._use_pygame = False
        self._sounds: dict[str, object] = {}
        self._paplay = shutil.which("paplay")
        self._init_backend()

    def _init_backend(self) -> None:
        try:
            import pygame

            self._ensure_mixer(pygame)
            self._use_pygame = True
            for wav in self._sounds_dir.glob("*.wav"):
                self._sounds[wav.stem] = pygame.mixer.Sound(str(wav))
        except Exception:  # noqa: BLE001 — mixer/display optional at edge
            self._use_pygame = False
            self._sounds.clear()

    @staticmethod
    def _ensure_mixer(pygame_mod: object) -> None:
        mixer = getattr(pygame_mod, "mixer", None)
        if mixer is None:
            msg = "pygame.mixer unavailable"
            raise RuntimeError(msg)
        get_init = getattr(mixer, "get_init", None)
        init = getattr(mixer, "init", None)
        if not callable(get_init) or not callable(init):
            msg = "pygame.mixer API incomplete"
            raise RuntimeError(msg)
        if get_init() is None:
            init(frequency=22050, size=-16, channels=1, buffer=512)

    def play(self, sound_id: str) -> None:
        if self._muted:
            return
        if self._use_pygame and sound_id in self._sounds:
            sound = self._sounds[sound_id]
            play = getattr(sound, "play", None)
            if callable(play):
                play()
            return
        path = self._sounds_dir / f"{sound_id}.wav"
        if self._paplay and path.exists():
            subprocess.Popen(  # noqa: S603 — fixed binary, user path under assets
                [self._paplay, str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def set_muted(self, muted: bool) -> None:
        self._muted = muted

    def is_muted(self) -> bool:
        return self._muted

    def toggle_mute(self) -> bool:
        self._muted = not self._muted
        return self._muted


class NullAudio:
    """Silent audio port for headless runs / tests."""

    def __init__(self) -> None:
        self._muted = False

    def play(self, sound_id: str) -> None:
        del sound_id

    def set_muted(self, muted: bool) -> None:
        self._muted = muted

    def is_muted(self) -> bool:
        return self._muted

    def toggle_mute(self) -> bool:
        self._muted = not self._muted
        return self._muted
