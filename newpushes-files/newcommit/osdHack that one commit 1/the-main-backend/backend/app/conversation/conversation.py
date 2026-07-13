"""Defines the Conversation value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Conversation:
    """A single deterministic memory-sharing event between two agents.

    Attributes:
        speaker_id: agent_id of whoever is sharing the memory.
        listener_id: agent_id of whoever is receiving the memory.
        memory_id: id of the Memory being shared.
        timestamp: Simulation time at which the conversation happened.
    """

    speaker_id: str
    listener_id: str
    memory_id: str
    timestamp: float
