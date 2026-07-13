"""Defines the Memory value object with cognitive attributes."""

from dataclasses import dataclass, field
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
        subject_id: Optional ID of the subject of this memory.
        emotion: Emotional resonance associated with this memory (e.g. concerned, curious).
        importance: Numerical score representing importance, in the range [0.0, 1.0].
        participants: List of agent names involved in the event.
        location: Name of the location where the event took place.
        tags: Categorical tags for indexing (e.g. gossip, crime).
    """

    id: str
    summary: str
    type: MemoryType
    source: str
    timestamp: float
    confidence: float
    shared: bool = False
    subject_id: str | None = None
    emotion: str = "neutral"
    importance: float = 0.5
    participants: list[str] = field(default_factory=list)
    location: str = "Unknown"
    tags: list[str] = field(default_factory=list)
