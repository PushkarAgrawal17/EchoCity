"""Defines the Location value object."""

from dataclasses import dataclass

from app.simulation.location_type import LocationType


@dataclass(frozen=True)
class Location:
    """An immutable place in the simulation that agents can occupy.

    Attributes:
        id: Unique identifier for this location.
        name: Human-readable display name.
        type: The category of location (e.g. CAFE, COURT).
    """

    id: str
    name: str
    type: LocationType