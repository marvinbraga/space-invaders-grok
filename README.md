# Space Invaders

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![pygame](https://img.shields.io/badge/pygame-2.5%2B-green.svg)](https://www.pygame.org/)
[![uv](https://img.shields.io/badge/uv-package%20manager-de5fe9.svg)](https://github.com/astral-sh/uv)
[![pytest](https://img.shields.io/badge/pytest-cov%20≥85%25-brightgreen.svg)](https://docs.pytest.org/)
[![mypy](https://img.shields.io/badge/mypy-strict-blue.svg)](https://mypy-lang.org/)
[![ruff](https://img.shields.io/badge/ruff-lint%20%2B%20format-fcc21b.svg)](https://docs.astral.sh/ruff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Classic **Taito 1978 Space Invaders** clone in pure Python OOP with Clean Architecture.
Domain logic is framework-free; pygame is an adapter at the edge.

## Features

- 5×11 alien formation, classic scoring (30 / 20 / 10)
- One player bullet at a time, 3 lives, extra life at 1 500 points (once)
- Group march, edge reverse + drop, acceleration as aliens die
- Destructible bunkers rebuilt each wave
- UFO with 15-value ROM score table
- Progressive difficulty by wave
- Persistent HI-SCORE on disk
- Pixel sprites (programmatic), colorful palette
- WAV SFX via pygame.mixer with `paplay` fallback

## Install & run

Requires **Python 3.11+** and [uv](https://github.com/astral-sh/uv).

```bash
cd space-invaders-grok   # or this repo root
uv sync
uv run python scripts/generate_sounds.py   # once: create assets/sounds/*.wav
uv run python -m space_invaders
```

## Controls

| Key | Action |
|-----|--------|
| ← → or A D | Move |
| Space | Fire (also starts from menu) |
| Enter | Start / confirm |
| P | Pause / resume |
| Ctrl+R | Restart run |
| M | Mute / unmute |
| ESC | Return to menu (keeps new HI-SCORE if set) |
| Ctrl+Q / window close | Quit |

## Architecture

```
src/space_invaders/
  domain/         # pure rules, entities, GoF patterns — no pygame
  application/    # use cases: high score, audio event bridge
  adapters/       # pygame render/input, file score repo, audio
  main.py         # composition root (wires ports → adapters)
tests/domain/     # TDD suite, ≥85% branch coverage on domain
assets/sounds/    # regenerable WAVs
scripts/          # sound generator
```

### Design patterns (real usages)

| Pattern | Where |
|---------|--------|
| **State** | `MenuState`, `PlayingState`, `PausedState`, `GameOverState` |
| **Strategy** | `WaveDifficulty` — step/fire timing by wave & alive count |
| **Observer** | `EventPublisher` + `AudioEventBridge` |
| **Factory** | Formation, bunker, bullet factories |
| **Command** | `InputCommand` / `CommandKind` |
| **Template Method** | `WaveTemplate.setup_wave` skeleton |
| **Ports** | `ScoreRepository`, `AudioPort`, `ClockPort` |

**Facade is forbidden** — composition root in `main.py` injects adapters directly.

### Game rules (classic)

- Formation: 5 rows × 11 columns
- Scores: top row 30, middle 20, bottom 10
- Game over: 0 lives **or** invasion (aliens reach the player line)
- UFO scores rotate through ROM table:  
  `100,50,50,100,150,100,100,50,300,100,100,100,50,150,100`

## Sound generation

```bash
uv run python scripts/generate_sounds.py
```

Writes retro square/noise WAVs into `assets/sounds/`:

`shot`, `alien_hit`, `player_hit`, `march`, `ufo`, `ufo_hit`, `wave_clear`, `game_over`

Playback prefers `pygame.mixer`; if unavailable, falls back to `paplay` when present.

## Quality gates

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
uv run pytest --cov=space_invaders.domain --cov-branch --cov-fail-under=85 -q
```

## HI-SCORE location

`~/.local/share/space-invaders-grok/highscore.json`

## License

MIT © 2026 Marvin Braga — see [LICENSE](LICENSE).
