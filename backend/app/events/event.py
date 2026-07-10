"""Event: a single occurrence in the simulation, carried by the EventBus."""

import uuid
from dataclasses import dataclass, field
from typing import Any

from app.events.event_type import EventType


@dataclass
class Event:
    """An immutable record of something that happened in the simulation.

    Attributes:
        event_type: The kind of event.
        timestamp: Simulation time at which the event occurred (in the
            same units as ``Clock.current_time``). Supplied by the caller
            rather than auto-generated from the wall clock — the
            simulation has its own notion of time, and Event should not
            silently couple itself to real-world time.
        payload: Arbitrary event-specific data. Deliberately untyped
            (``dict[str, Any]``) since each EventType carries different
            information and this module must not know about any of them.
        event_id: Unique identifier, auto-generated.
    """

    event_type: EventType
    timestamp: float
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))