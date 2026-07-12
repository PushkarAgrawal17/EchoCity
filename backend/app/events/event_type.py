"""EventType: kinds of events that can occur in the simulation.

Only events actually produced by subsystems built so far. Gameplay events
(crime, conversation, relationship, etc.) are added by the milestones that
introduce them — not anticipated here.
"""

from enum import Enum, auto


class EventType(Enum):
    """Enumerates the kinds of events the EventBus can carry."""

    WORLD_STARTED = auto()
    WORLD_STOPPED = auto()
    TICK = auto()
    AGENT_REGISTERED = auto()
    AGENT_REMOVED = auto()
