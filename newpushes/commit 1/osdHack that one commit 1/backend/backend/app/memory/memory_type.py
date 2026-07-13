"""Defines the categories of Memory an agent can hold."""

from enum import Enum


class MemoryType(Enum):
    """Classifies how a Memory was obtained.

    WITNESS: Directly observed by the agent.
    HEARD: Told to the agent by another agent (gossip/rumor).
    PERSONAL: Relates to the agent's own experience or feelings.
    EVIDENCE: Formally significant to the investigation/court.
    """

    WITNESS = "witness"
    HEARD = "heard"
    PERSONAL = "personal"
    EVIDENCE = "evidence"
