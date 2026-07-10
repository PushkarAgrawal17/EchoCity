"""Clock: tracks simulation time.

Standalone component — no knowledge of World, SimulationEngine, or any
other subsystem. It only converts elapsed ticks into simulation time.
"""

DEFAULT_TICK_DURATION_SECONDS = 60.0  # 1 tick = 1 in-simulation minute


class Clock:
    """Tracks simulation time as a multiple of a configurable tick duration.

    Simulation time is derived, not stored independently: it is always
    ``tick_count * tick_duration_seconds``. This guarantees time and tick
    count can never drift apart.

    Attributes:
        tick_duration_seconds: Simulation seconds represented by one tick.
    """

    def __init__(self, tick_duration_seconds: float = DEFAULT_TICK_DURATION_SECONDS) -> None:
        """Create a Clock at time zero.

        Args:
            tick_duration_seconds: Simulation seconds per tick. Must be
                positive.

        Raises:
            ValueError: If ``tick_duration_seconds`` is not positive.
        """
        if tick_duration_seconds <= 0:
            raise ValueError("tick_duration_seconds must be positive.")

        self.tick_duration_seconds = tick_duration_seconds
        self._tick_count = 0

    @property
    def tick_count(self) -> int:
        """Number of ticks elapsed since the clock started or was reset."""
        return self._tick_count

    @property
    def current_time(self) -> float:
        """Total simulation time elapsed, in simulation seconds."""
        return self._tick_count * self.tick_duration_seconds

    def advance(self) -> None:
        """Advance the clock by exactly one tick."""
        self._tick_count += 1

    def reset(self) -> None:
        """Reset the clock back to tick zero."""
        self._tick_count = 0