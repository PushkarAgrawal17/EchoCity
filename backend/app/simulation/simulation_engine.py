"""SimulationEngine: drives the simulation loop.

This module owns *when* ticks happen. It knows nothing about *what*
happens inside a tick — that is entirely World's responsibility. No Clock,
Scheduler, EventBus, or threading/async is introduced here; those belong
to later PRs.
"""

import logging
import time
from collections.abc import Callable

from app.simulation.world import World

logger = logging.getLogger(__name__)

DEFAULT_TICK_INTERVAL_SECONDS = 1.0


class SimulationEngine:
    """Drives ``World`` forward at a configurable, fixed tick interval.

    The engine runs a simple blocking loop: sleep for ``tick_interval``
    seconds, then call ``world.tick()``, repeat until stopped. It contains
    no simulation logic of its own.

    Attributes:
        world: The World instance this engine drives.
        tick_interval: Seconds to wait between ticks.
    """

    def __init__(
        self,
        world: World,
        tick_interval: float = DEFAULT_TICK_INTERVAL_SECONDS,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        """Create a SimulationEngine bound to a World.

        Args:
            world: The World instance to drive.
            tick_interval: Seconds to sleep between ticks. Must be positive.
            sleep_fn: Sleep function to call between ticks. Overridable so
                tests can run the loop without real wall-clock delays.

        Raises:
            ValueError: If ``tick_interval`` is not positive.
        """
        if tick_interval <= 0:
            raise ValueError("tick_interval must be positive.")

        self.world = world
        self.tick_interval = tick_interval
        self._sleep_fn = sleep_fn

    def start(self) -> None:
        """Start the underlying world.

        Idempotent, delegating entirely to ``World``'s own idempotent
        ``start()`` — ``World`` is the single source of truth for
        simulation lifecycle state.
        """
        self.world.start()
        logger.info("SimulationEngine started (tick_interval=%.3fs).", self.tick_interval)

    def stop(self) -> None:
        """Stop the underlying world.

        Causes ``run()`` to exit after its current sleep. Idempotent via
        ``World.stop()``.
        """
        self.world.stop()
        logger.info("SimulationEngine stopped.")

    def run(self) -> None:
        """Run the simulation loop until the world is stopped.

        Blocking call: repeatedly sleeps for ``tick_interval`` seconds then
        ticks the world, for as long as ``world.is_running`` is ``True``.
        Must be started with ``start()`` first, otherwise it returns
        immediately without ticking.
        """
        if not self.world.is_running:
            logger.warning("SimulationEngine.run() called before start(); returning immediately.")
            return

        while self.world.is_running:
            self._sleep_fn(self.tick_interval)
            if not self.world.is_running:
                break
            self.world.tick()