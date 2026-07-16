# PROJECT_RULES — Space Invaders (Taito 1978 clone)

## Stack
- Python 3.12+ (3.11 minimum), `uv`, pygame
- Clean Architecture: domain (pure) → application → adapters (pygame)
- OOP, SOLID, Clean Code; GoF: State, Strategy, Observer, Factory, Command, Template Method, Ports
- **Forbidden: Facade pattern**

## Quality gates
- TDD on domain layer first (RED/GREEN)
- `mypy --strict` clean
- `ruff` with max complexity ≤ 10
- pytest domain coverage ≥ 85% (`--cov-fail-under=85` on domain package)
- No license header spam required on every file; MIT LICENSE at repo root

## Game rules (classic)
- Alien formation 5×11
- Scores: bottom rows 10, middle 20, top 30
- One player bullet at a time; 3 lives; extra life at 1500
- Group movement, drop on edge, speed-up as aliens die
- Destructible bunkers rebuilt each wave
- UFO with 15-value ROM score table
- Game over: lives exhausted or invasion (aliens reach player line)
- HI-SCORE persistent on disk

## Product
- Readable menu (no HI-SCORE overflow/duplication)
- Pixel sprites; colorful
- Controls: arrows/A-D, Space, Enter; P pause; Ctrl+R restart; M mute; ESC → menu (preserve new high score if set)
- Progressive difficulty by wave
- WAV SFX in assets/sounds/, regenerable via scripts/generate_sounds.py
- pygame.mixer with paplay fallback
- SFX: shot, hits, march, UFO, wave clear, game over
- README with tech badges; MIT; proper .gitignore
- Publish: git@github.com:marvinbraga/space-invaders-grok.git on main

## Layout
```
src/space_invaders/
  domain/          # pure game logic, no pygame
  application/     # use cases / services
  adapters/        # pygame, audio, persistence
  main.py
tests/domain/
assets/sounds/
scripts/generate_sounds.py
```

## Constraints
- Implement FROM SCRATCH. Do NOT read sibling projects (../gpt, ../grok, ../opus).
- Prefer composition and ports over inheritance depth.
