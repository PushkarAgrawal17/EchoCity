"""Console demonstration of the integrated EchoCity simulation.

Run with:
    uv run python scripts/demo.py

Drives World directly (not through SimulationEngine) so the demo runs
instantly and deterministically rather than sleeping in real time between
ticks — SimulationEngine's job is real-time pacing, which isn't useful for
a quick console demonstration.
"""

import logging

from app.agents.agent import Agent
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.events.event import Event
from app.events.event_type import EventType
from app.simulation.location import Location
from app.simulation.location_manager import LocationManager
from app.simulation.location_type import LocationType
from app.simulation.world import World

TICKS_TO_RUN = 5


def on_tick(event: Event) -> None:
    """Print progress each time a TICK event is published."""
    print(f"[tick {event.payload['tick_count']}] simulation time = {event.timestamp:.0f}s")


def main() -> None:
    """Build a small World, register an agent, schedule a task, and run it."""
    setup_logging(get_settings())
    logging.getLogger(__name__).info("Starting EchoCity console demo.")

    world = World()
    world.event_bus.subscribe(EventType.TICK, on_tick)

    location_manager = LocationManager()

    location_manager.register_location(
        Location(
            id="cafe",
            name="The Cafe",
            type=LocationType.CAFE,
        )
    )

    cafe = location_manager.get_location("cafe")

    noah = Agent(
        agent_id="npc_noah",
        name="Noah",
        location=cafe,
    )

    world.agent_manager.register(noah)
    print(f"Registered agent: {noah.name} at {noah.location}")

    def greet() -> None:
        print(f"[scheduled task] {noah.name} says hello.")

    world.scheduler.schedule_at(run_at=world.clock.current_time + 120.0, task=greet)

    world.start()
    for _ in range(TICKS_TO_RUN):
        world.tick()
    world.stop()

    print(f"Demo finished after {world.tick_count} ticks.")


if __name__ == "__main__":
    main()