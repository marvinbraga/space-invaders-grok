"""Domain events published by the game session (Observer pattern)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Base marker for all domain events."""


@dataclass(frozen=True, slots=True)
class PlayerShot(DomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class AlienHit(DomainEvent):
    points: int
    row: int
    col: int


@dataclass(frozen=True, slots=True)
class PlayerHit(DomainEvent):
    lives_remaining: int


@dataclass(frozen=True, slots=True)
class UfoSpawned(DomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class UfoHit(DomainEvent):
    points: int


@dataclass(frozen=True, slots=True)
class UfoDespawned(DomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class WaveCleared(DomainEvent):
    wave: int


@dataclass(frozen=True, slots=True)
class WaveStarted(DomainEvent):
    wave: int


@dataclass(frozen=True, slots=True)
class GameOverEvent(DomainEvent):
    score: int
    is_high_score: bool


@dataclass(frozen=True, slots=True)
class ExtraLifeAwarded(DomainEvent):
    lives: int


@dataclass(frozen=True, slots=True)
class AlienMarched(DomainEvent):
    remaining: int


@dataclass(frozen=True, slots=True)
class BunkerDamaged(DomainEvent):
    bunker_index: int


@dataclass(frozen=True, slots=True)
class ScoreChanged(DomainEvent):
    score: int
    high_score: int


class EventListener(Protocol):
    def on_event(self, event: DomainEvent) -> None: ...


class EventPublisher:
    """Simple synchronous event bus (Observer)."""

    def __init__(self) -> None:
        self._listeners: list[EventListener] = []

    def subscribe(self, listener: EventListener) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: EventListener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def publish(self, event: DomainEvent) -> None:
        for listener in list(self._listeners):
            listener.on_event(event)

    def clear(self) -> None:
        self._listeners.clear()
