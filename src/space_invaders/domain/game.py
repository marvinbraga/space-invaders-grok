"""Game session — Template Method for wave lifecycle + state machine."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod

from space_invaders.domain.commands import InputCommand
from space_invaders.domain.constants import (
    EXTRA_LIFE_SCORE,
    INITIAL_LIVES,
    PLAYER_START_X,
    PLAYER_Y,
    PLAYFIELD_WIDTH,
    UFO_ROM_SCORES,
    UFO_SPAWN_MAX,
    UFO_SPAWN_MIN,
    UFO_WIDTH,
    UFO_Y,
)
from space_invaders.domain.entities import Bullet, Bunker, Player, Ufo
from space_invaders.domain.events import (
    AlienHit,
    AlienMarched,
    BunkerDamaged,
    EventPublisher,
    ExtraLifeAwarded,
    GameOverEvent,
    PlayerHit,
    PlayerShot,
    ScoreChanged,
    UfoDespawned,
    UfoHit,
    UfoSpawned,
    WaveCleared,
    WaveStarted,
)
from space_invaders.domain.factories import (
    BulletFactory,
    BunkerFactory,
    DefaultBulletFactory,
    DefaultBunkerFactory,
    DefaultFormationFactory,
    FormationFactory,
)
from space_invaders.domain.formation import AlienFormation
from space_invaders.domain.states import GameOverState, GameState, MenuState, Phase, PlayingState
from space_invaders.domain.strategies import DifficultyStrategy, difficulty_for_wave
from space_invaders.domain.value_objects import Direction, Position, Score


class WaveTemplate(ABC):
    """Template Method: fixed wave setup skeleton with overridable hooks."""

    def setup_wave(self, session: GameSession, wave: int) -> None:
        session.apply_difficulty(difficulty_for_wave(wave))
        session.replace_formation(self.build_formation(session))
        session.replace_bunkers(self.build_bunkers(session))
        session.clear_projectiles()
        session.reset_ufo()
        self.after_wave_ready(session, wave)

    @abstractmethod
    def build_formation(self, session: GameSession) -> AlienFormation: ...

    @abstractmethod
    def build_bunkers(self, session: GameSession) -> list[Bunker]: ...

    def after_wave_ready(self, session: GameSession, wave: int) -> None:
        session.publish_wave_started(wave)


class ClassicWaveSetup(WaveTemplate):
    def build_formation(self, session: GameSession) -> AlienFormation:
        return AlienFormation(session.formation_factory.create())

    def build_bunkers(self, session: GameSession) -> list[Bunker]:
        return session.bunker_factory.create()


class GameSession:
    """Core playable session. No pygame; pure domain."""

    def __init__(
        self,
        events: EventPublisher | None = None,
        formation_factory: FormationFactory | None = None,
        bunker_factory: BunkerFactory | None = None,
        bullet_factory: BulletFactory | None = None,
        wave_setup: WaveTemplate | None = None,
        rng: random.Random | None = None,
        high_score: int = 0,
    ) -> None:
        self._events = events if events is not None else EventPublisher()
        self.formation_factory = (
            formation_factory if formation_factory is not None else DefaultFormationFactory()
        )
        self.bunker_factory = (
            bunker_factory if bunker_factory is not None else DefaultBunkerFactory()
        )
        self._bullet_factory = (
            bullet_factory if bullet_factory is not None else DefaultBulletFactory()
        )
        self._wave_setup = wave_setup if wave_setup is not None else ClassicWaveSetup()
        self._rng = rng if rng is not None else random.Random()
        self._high_score = max(0, high_score)
        self._score = Score(0)
        self._wave = 0
        self._player = Player(
            position=Position(PLAYER_START_X, float(PLAYER_Y)),
            lives=INITIAL_LIVES,
        )
        self._formation = AlienFormation([])
        self._bunkers: list[Bunker] = []
        self._player_bullet: Bullet | None = None
        self._alien_bullets: list[Bullet] = []
        self._ufo: Ufo | None = None
        self._ufo_score_index = 0
        self._ufo_timer = self._rng.uniform(UFO_SPAWN_MIN, UFO_SPAWN_MAX)
        self._difficulty: DifficultyStrategy = difficulty_for_wave(1)
        self._step_timer = 0.0
        self._fire_timer = 0.0
        self._moving_left = False
        self._moving_right = False
        self._extra_life_awarded = False
        self._quit_requested = False
        self._mute_toggled = False
        self._state: GameState = MenuState()
        self._game_over_finalized = False

    # --- queries ---

    @property
    def phase(self) -> Phase:
        return self._state.phase

    @property
    def score(self) -> int:
        return int(self._score)

    @property
    def high_score(self) -> int:
        return self._high_score

    @property
    def wave(self) -> int:
        return self._wave

    @property
    def player(self) -> Player:
        return self._player

    @property
    def formation(self) -> AlienFormation:
        return self._formation

    @property
    def bunkers(self) -> list[Bunker]:
        return self._bunkers

    @property
    def player_bullet(self) -> Bullet | None:
        return self._player_bullet

    @property
    def alien_bullets(self) -> list[Bullet]:
        return list(self._alien_bullets)

    @property
    def ufo(self) -> Ufo | None:
        return self._ufo

    @property
    def events(self) -> EventPublisher:
        return self._events

    @property
    def quit_requested(self) -> bool:
        return self._quit_requested

    @property
    def mute_toggled(self) -> bool:
        return self._mute_toggled

    def consume_mute_toggle(self) -> bool:
        flagged = self._mute_toggled
        self._mute_toggled = False
        return flagged

    def sync_high_score(self, high_score: int) -> None:
        """Allow composition root to reflect persisted HI-SCORE."""
        if high_score > self._high_score:
            self._high_score = high_score

    # --- state / input ---

    def handle(self, command: InputCommand) -> None:
        self._state.handle(self, command)

    def update(self, dt: float) -> None:
        if dt < 0:
            msg = f"dt must be non-negative, got {dt}"
            raise ValueError(msg)
        self._state.update(self, dt)

    def transition_to(self, state: GameState) -> None:
        self._state = state
        state.enter(self)

    def begin_play(self) -> None:
        self._reset_run()
        self._wave = 1
        self._wave_setup.setup_wave(self, self._wave)
        self.transition_to(PlayingState())

    def restart(self) -> None:
        self.begin_play()

    def return_to_menu(self) -> None:
        self._persist_high_score_if_needed()
        self._reset_run()
        self.transition_to(MenuState())

    def request_quit(self) -> None:
        self._persist_high_score_if_needed()
        self._quit_requested = True

    def toggle_mute_flag(self) -> None:
        self._mute_toggled = True

    def set_moving_left(self, active: bool) -> None:
        self._moving_left = active

    def set_moving_right(self, active: bool) -> None:
        self._moving_right = active

    def try_fire(self) -> None:
        if self._player_bullet is not None and self._player_bullet.active:
            return
        bullet = self._bullet_factory.player_bullet(self._player)
        self._player_bullet = bullet
        self._events.publish(PlayerShot())

    # --- wave template collaborators ---

    def apply_difficulty(self, difficulty: DifficultyStrategy) -> None:
        self._difficulty = difficulty
        self._step_timer = 0.0
        self._fire_timer = 0.0

    def replace_formation(self, formation: AlienFormation) -> None:
        self._formation = formation

    def replace_bunkers(self, bunkers: list[Bunker]) -> None:
        self._bunkers = bunkers

    def clear_projectiles(self) -> None:
        self._player_bullet = None
        self._alien_bullets.clear()

    def reset_ufo(self) -> None:
        self._ufo = None
        self._ufo_timer = self._rng.uniform(UFO_SPAWN_MIN, UFO_SPAWN_MAX)

    def publish_wave_started(self, wave: int) -> None:
        self._events.publish(WaveStarted(wave=wave))

    def finalize_game_over(self) -> None:
        if self._game_over_finalized:
            return
        self._game_over_finalized = True
        is_hi = self._score.value > 0 and self._score.value >= self._high_score
        self._persist_high_score_if_needed()
        self._events.publish(GameOverEvent(score=self._score.value, is_high_score=is_hi))

    # --- play loop ---

    def tick_play(self, dt: float) -> None:
        self._player.tick_invulnerability(dt)
        self._move_player(dt)
        self._update_bullets(dt)
        self._march_aliens(dt)
        self._alien_fire(dt)
        self._update_ufo(dt)
        self._resolve_collisions()
        self._check_wave_clear()
        self._check_game_over()

    def _move_player(self, dt: float) -> None:
        if self._moving_left and not self._moving_right:
            self._player.move(Direction.LEFT, dt)
        elif self._moving_right and not self._moving_left:
            self._player.move(Direction.RIGHT, dt)

    def _update_bullets(self, dt: float) -> None:
        if self._player_bullet is not None:
            self._player_bullet.update(dt)
            if not self._player_bullet.active:
                self._player_bullet = None
        for bullet in self._alien_bullets:
            bullet.update(dt)
        self._alien_bullets = [b for b in self._alien_bullets if b.active]

    def _march_aliens(self, dt: float) -> None:
        alive = self._formation.count_alive()
        if alive == 0:
            return
        interval = self._difficulty.step_interval(alive, self._formation.total())
        self._step_timer += dt
        if self._step_timer < interval:
            return
        self._step_timer = 0.0
        self._formation.step()
        self._events.publish(AlienMarched(remaining=self._formation.count_alive()))

    def _alien_fire(self, dt: float) -> None:
        max_bullets = self._difficulty.max_alien_bullets()
        if len(self._alien_bullets) >= max_bullets:
            return
        self._fire_timer += dt
        if self._fire_timer < self._difficulty.alien_fire_interval():
            return
        self._fire_timer = 0.0
        shooters = self._formation.shooters()
        if not shooters:
            return
        alien = self._rng.choice(shooters)
        self._alien_bullets.append(self._bullet_factory.alien_bullet(alien))

    def _update_ufo(self, dt: float) -> None:
        ufo = self._ufo
        if ufo is not None:
            self._tick_active_ufo(ufo, dt)
            return
        if self._formation.count_alive() < 8:
            return
        self._ufo_timer -= dt
        if self._ufo_timer > 0:
            return
        self._spawn_ufo()

    def _tick_active_ufo(self, ufo: Ufo, dt: float) -> None:
        if ufo.active:
            ufo.update(dt, self._difficulty.ufo_speed())
        if ufo.active:
            return
        self._events.publish(UfoDespawned())
        self._ufo = None
        self._ufo_timer = self._rng.uniform(UFO_SPAWN_MIN, UFO_SPAWN_MAX)

    def _spawn_ufo(self) -> None:
        going_right = self._rng.random() < 0.5
        if going_right:
            pos = Position(float(-UFO_WIDTH), float(UFO_Y))
            direction = Direction.RIGHT
        else:
            pos = Position(float(PLAYFIELD_WIDTH), float(UFO_Y))
            direction = Direction.LEFT
        self._ufo = Ufo(position=pos, direction=direction, score_index=self._ufo_score_index)
        self._events.publish(UfoSpawned())

    def _resolve_collisions(self) -> None:
        self._player_bullet_hits()
        self._alien_bullet_hits()

    def _player_bullet_hits(self) -> None:
        bullet = self._player_bullet
        if bullet is None or not bullet.active:
            return
        b = bullet.bounds()
        if self._ufo is not None and self._ufo.active and b.intersects(self._ufo.bounds()):
            points = UFO_ROM_SCORES[self._ufo_score_index % len(UFO_ROM_SCORES)]
            self._ufo_score_index = (self._ufo_score_index + 1) % len(UFO_ROM_SCORES)
            self._ufo.deactivate()
            self._ufo = None
            bullet.deactivate()
            self._player_bullet = None
            self._add_score(points)
            self._events.publish(UfoHit(points=points))
            self._ufo_timer = self._rng.uniform(UFO_SPAWN_MIN, UFO_SPAWN_MAX)
            return
        for alien in self._formation.living():
            if b.intersects(alien.bounds()):
                points = alien.kill()
                bullet.deactivate()
                self._player_bullet = None
                self._add_score(points)
                self._events.publish(AlienHit(points=points, row=alien.row, col=alien.col))
                return
        for bunker in self._bunkers:
            if bunker.collides_rect(b):
                bunker.damage_at(b.x + b.width / 2, b.y + b.height / 2)
                bullet.deactivate()
                self._player_bullet = None
                self._events.publish(BunkerDamaged(bunker_index=bunker.index))
                return

    def _alien_bullet_hits(self) -> None:
        for bullet in list(self._alien_bullets):
            if not bullet.active:
                continue
            b = bullet.bounds()
            if not self._player.invulnerable and b.intersects(self._player.bounds()):
                bullet.deactivate()
                self._on_player_hit()
                continue
            for bunker in self._bunkers:
                if bunker.collides_rect(b):
                    bunker.damage_at(b.x + b.width / 2, b.y + b.height / 2)
                    bullet.deactivate()
                    self._events.publish(BunkerDamaged(bunker_index=bunker.index))
                    break
        self._alien_bullets = [bl for bl in self._alien_bullets if bl.active]

    def _on_player_hit(self) -> None:
        lives = self._player.lose_life()
        self._events.publish(PlayerHit(lives_remaining=lives))
        self.clear_projectiles()
        if lives > 0:
            self._player.position = Position(PLAYER_START_X, float(PLAYER_Y))
            self._player.start_invulnerability()
        else:
            self.transition_to(GameOverState())

    def _check_wave_clear(self) -> None:
        if self._state.phase is not Phase.PLAYING:
            return
        if not self._formation.is_cleared():
            return
        self._events.publish(WaveCleared(wave=self._wave))
        self._wave += 1
        self._wave_setup.setup_wave(self, self._wave)

    def _check_game_over(self) -> None:
        if self._state.phase is not Phase.PLAYING:
            return
        if self._player.lives <= 0:
            self.transition_to(GameOverState())
            return
        if self._formation.has_invaded():
            self._player.lives = 0
            self.transition_to(GameOverState())

    def _add_score(self, points: int) -> None:
        self._score = self._score.add(points)
        if not self._extra_life_awarded and self._score.value >= EXTRA_LIFE_SCORE:
            self._extra_life_awarded = True
            self._player.gain_life()
            self._events.publish(ExtraLifeAwarded(lives=self._player.lives))
        if self._score.value > self._high_score:
            self._high_score = self._score.value
        self._events.publish(ScoreChanged(score=self._score.value, high_score=self._high_score))

    def _persist_high_score_if_needed(self) -> None:
        if self._score.value > self._high_score:
            self._high_score = self._score.value

    def _reset_run(self) -> None:
        self._score = Score(0)
        self._wave = 0
        self._player = Player(
            position=Position(PLAYER_START_X, float(PLAYER_Y)),
            lives=INITIAL_LIVES,
        )
        self._formation = AlienFormation([])
        self._bunkers = []
        self.clear_projectiles()
        self.reset_ufo()
        self._ufo_score_index = 0
        self._moving_left = False
        self._moving_right = False
        self._extra_life_awarded = False
        self._game_over_finalized = False
        self._step_timer = 0.0
        self._fire_timer = 0.0
