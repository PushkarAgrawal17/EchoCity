"""Defines the set of location categories available in the simulation."""

from enum import Enum


class LocationType(Enum):
    """Identifies which kind of place a Location represents.

    The MVP world contains exactly two location types: the Cafe,
    where NPCs interact and the investigation unfolds, and the Court,
    where the player presents evidence and receives a verdict.
    """

    CAFE = "cafe"
    COURT = "court"
    POLICE_STATION = "police_station"
    BANK = "bank"
    HOSPITAL = "hospital"
    SCHOOL = "school"
    GARAGE = "garage"
    APARTMENT_BUILDING = "apartment_building"
    PARK = "park"
