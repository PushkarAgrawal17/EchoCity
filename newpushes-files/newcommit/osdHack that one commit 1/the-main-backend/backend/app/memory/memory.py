"""Defines the Memory value object."""

from dataclasses import dataclass

from app.memory.memory_type import MemoryType


@dataclass(frozen=True)
class Memory:
    """An immutable record of something an agent knows.

    Attributes:
        id: Unique identifier for this memory.
        summary: Short human-readable description of what is known.
        type: The MemoryType classifying how it was obtained.
        source: Identifier of who/what this memory came from
            (e.g. an agent_id, or "self" for direct observation).
        timestamp: Simulation time at which the memory was formed.
        confidence: How certain the agent is this memory is true,
            in the range [0.0, 1.0].
        shared: Whether this memory has been told to another agent.
    """

    id: str
    summary: str
    type: MemoryType
    source: str
    timestamp: float
    confidence: float
    shared: bool = False
    subject_id: str | None = None
