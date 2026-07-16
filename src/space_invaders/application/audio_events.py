"""Observer that maps domain events to AudioPort sound IDs."""

from __future__ import annotations

from space_invaders.domain.events import (
    AlienHit,
    AlienMarched,
    DomainEvent,
    GameOverEvent,
    PlayerHit,
    PlayerShot,
    UfoHit,
    UfoSpawned,
    WaveCleared,
)
from space_invaders.domain.ports import AudioPort

# Sound ID constants used by adapters
SOUND_SHOT = "shot"
SOUND_ALIEN_HIT = "alien_hit"
SOUND_PLAYER_HIT = "player_hit"
SOUND_MARCH = "march"
SOUND_UFO = "ufo"
SOUND_UFO_HIT = "ufo_hit"
SOUND_WAVE_CLEAR = "wave_clear"
SOUND_GAME_OVER = "game_over"


class AudioEventBridge:
    """EventListener adapter between domain events and AudioPort."""

    def __init__(self, audio: AudioPort) -> None:
        self._audio = audio
        self._march_counter = 0

    def on_event(self, event: DomainEvent) -> None:
        if isinstance(event, PlayerShot):
            self._audio.play(SOUND_SHOT)
        elif isinstance(event, AlienHit):
            self._audio.play(SOUND_ALIEN_HIT)
        elif isinstance(event, PlayerHit):
            self._audio.play(SOUND_PLAYER_HIT)
        elif isinstance(event, AlienMarched):
            self._march_counter = (self._march_counter + 1) % 4
            self._audio.play(SOUND_MARCH)
        elif isinstance(event, UfoSpawned):
            self._audio.play(SOUND_UFO)
        elif isinstance(event, UfoHit):
            self._audio.play(SOUND_UFO_HIT)
        elif isinstance(event, WaveCleared):
            self._audio.play(SOUND_WAVE_CLEAR)
        elif isinstance(event, GameOverEvent):
            self._audio.play(SOUND_GAME_OVER)
