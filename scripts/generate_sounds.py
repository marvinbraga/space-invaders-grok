#!/usr/bin/env python3
"""Generate retro 8-bit style WAV sound effects for Space Invaders.

Usage:
    uv run python scripts/generate_sounds.py
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 22050
OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "sounds"


def _write_wav(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            frames += struct.pack("<h", int(clamped * 32767))
        wf.writeframes(frames)


def _tone(
    freq: float,
    duration: float,
    volume: float = 0.4,
    decay: bool = True,
) -> list[float]:
    n = int(SAMPLE_RATE * duration)
    samples: list[float] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = (1.0 - t / duration) if decay else 1.0
        # square-ish wave for retro feel
        raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        samples.append(raw * volume * env)
    return samples


def _noise(duration: float, volume: float = 0.35) -> list[float]:
    n = int(SAMPLE_RATE * duration)
    samples: list[float] = []
    state = 1
    for i in range(n):
        # simple LFSR-ish pseudo noise
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        bit = 1.0 if (state >> 16) & 1 else -1.0
        env = 1.0 - (i / n)
        samples.append(bit * volume * env)
    return samples


def _slide(f0: float, f1: float, duration: float, volume: float = 0.35) -> list[float]:
    n = int(SAMPLE_RATE * duration)
    samples: list[float] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        frac = i / max(1, n - 1)
        freq = f0 + (f1 - f0) * frac
        env = 1.0 - frac
        raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        samples.append(raw * volume * env)
    return samples


def generate_all() -> None:
    sounds: dict[str, list[float]] = {
        "shot": _slide(880, 220, 0.08, 0.3),
        "alien_hit": _noise(0.12, 0.4) + _tone(120, 0.05, 0.2),
        "player_hit": _noise(0.35, 0.5) + _slide(200, 40, 0.25, 0.4),
        "march": _tone(90, 0.06, 0.25, decay=True),
        "ufo": _slide(400, 600, 0.15, 0.25) + _slide(600, 400, 0.15, 0.25),
        "ufo_hit": _slide(600, 100, 0.3, 0.4) + _noise(0.1, 0.3),
        "wave_clear": (
            _tone(262, 0.1, 0.3)
            + _tone(330, 0.1, 0.3)
            + _tone(392, 0.1, 0.3)
            + _tone(523, 0.2, 0.35)
        ),
        "game_over": (
            _tone(392, 0.2, 0.35)
            + _tone(349, 0.2, 0.35)
            + _tone(311, 0.2, 0.35)
            + _tone(262, 0.4, 0.4)
        ),
    }
    for name, samples in sounds.items():
        path = OUT_DIR / f"{name}.wav"
        _write_wav(path, samples)
        print(f"wrote {path}")


if __name__ == "__main__":
    generate_all()
