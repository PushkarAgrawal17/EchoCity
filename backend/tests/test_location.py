"""Unit tests for the Location subsystem."""

import pytest

from app.simulation.location import Location
from app.simulation.location_manager import LocationManager
from app.simulation.location_type import LocationType


def test_location_is_immutable() -> None:
    """Location should be frozen (immutable) once created."""
    location = Location(id="cafe", name="The Cafe", type=LocationType.CAFE)
    with pytest.raises(AttributeError):
        location.name = "Renamed"  # type: ignore[misc]


def test_register_and_get_location() -> None:
    """A registered location should be retrievable by id."""
    manager = LocationManager()
    cafe = Location(id="cafe", name="The Cafe", type=LocationType.CAFE)

    manager.register_location(cafe)

    assert manager.get_location("cafe") == cafe


def test_register_duplicate_id_raises() -> None:
    """Registering two locations with the same id should fail."""
    manager = LocationManager()
    cafe = Location(id="cafe", name="The Cafe", type=LocationType.CAFE)
    manager.register_location(cafe)

    duplicate = Location(id="cafe", name="Another Cafe", type=LocationType.CAFE)
    with pytest.raises(ValueError):
        manager.register_location(duplicate)


def test_get_unknown_location_raises() -> None:
    """Looking up an unregistered id should raise KeyError."""
    manager = LocationManager()
    with pytest.raises(KeyError):
        manager.get_location("nonexistent")


def test_list_locations_returns_all() -> None:
    """list_locations should return every registered location."""
    manager = LocationManager()
    cafe = Location(id="cafe", name="The Cafe", type=LocationType.CAFE)
    court = Location(id="court", name="The Court", type=LocationType.COURT)

    manager.register_location(cafe)
    manager.register_location(court)

    locations = manager.list_locations()

    assert len(locations) == 2
    assert cafe in locations
    assert court in locations


def test_list_locations_empty_by_default() -> None:
    """A fresh LocationManager should have no locations."""
    manager = LocationManager()
    assert manager.list_locations() == []