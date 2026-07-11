"""Defines the Evidence value object."""

from dataclasses import dataclass

from app.memory.memory import Memory


@dataclass(frozen=True)
class Evidence:
    """A Memory that the player has collected as evidence.

    Attributes:
        id: Unique identifier for this piece of evidence.
        memory: The original, immutable Memory being used as evidence.
        collected_at: Simulation time at which it was collected.
    """

    id: str
    memory: Memory
    collected_at: float
