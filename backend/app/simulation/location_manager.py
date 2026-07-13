"""Manages registration and lookup of all Locations in the simulation."""

from app.simulation.location import Location


class LocationManager:
    """Owns the set of all Locations that exist in the world.

    Responsible for registering locations and providing lookup by id.
    Does not own agents, movement, or any behavior beyond storage
    and retrieval of Location objects.
    """

    def __init__(self) -> None:
        """Initialize an empty location registry."""
        self._locations: dict[str, Location] = {}

    def register_location(self, location: Location) -> None:
        """Register a new location.

        Args:
            location: The Location to register.

        Raises:
            ValueError: If a location with the same id is already registered.
        """
        if location.id in self._locations:
            raise ValueError(f"Location with id '{location.id}' already registered.")
        self._locations[location.id] = location

    def get_location(self, location_id: str) -> Location:
        """Retrieve a location by its id.

        Args:
            location_id: The id of the location to retrieve.

        Returns:
            The matching Location.

        Raises:
            KeyError: If no location with the given id is registered.
        """
        if location_id not in self._locations:
            raise KeyError(f"No location registered with id '{location_id}'.")
        return self._locations[location_id]

    def list_locations(self) -> list[Location]:
        """Return all registered locations.

        Returns:
            A list of every registered Location.
        """
        return list(self._locations.values())

    def get(self, location_id: str | None) -> Location | None:
        """Safely retrieve a location by its id, returning None if not found or id is None."""
        if location_id is None:
            return None
        return self._locations.get(location_id)
