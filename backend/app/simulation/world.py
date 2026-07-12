"""The World: root object of the EchoCity simulation.

World owns every core subsystem built so far (Clock, Scheduler,
AgentManager, EventBus) and defines the tick lifecycle that drives them.
It still contains no gameplay, AI, relationships, memory, or conversation
logic — those belong to later milestones.
"""

import logging

from app.agents.agent_manager import AgentManager
from app.conversation.conversation_engine import ConversationEngine
from app.conversation.gossip_engine import GossipEngine
from app.events.event import Event
from app.events.event_bus import EventBus
from app.events.event_type import EventType
from app.memory.memory_manager import MemoryManager
from app.simulation.clock import Clock
from app.simulation.scheduler import Scheduler

logger = logging.getLogger(__name__)


class World:
    """Root object of the simulation.

    ``World`` is the single source of truth for simulation state and owns
    every subsystem below it. Nothing outside ``World`` should hold
    simulation state directly.

    Attributes:
        is_running: Whether the simulation is currently active.
        tick_count: Number of ticks executed since the world was created.
        clock: Tracks simulation time.
        scheduler: Executes tasks scheduled against ``clock``.
        agent_manager: Owns all registered agents.
        event_bus: Publishes simulation events to subscribers.
    """

    def __init__(
        self,
        clock: Clock | None = None,
        scheduler: Scheduler | None = None,
        agent_manager: AgentManager | None = None,
        event_bus: EventBus | None = None,
        memory_manager: MemoryManager | None = None,
        conversation_engine: ConversationEngine | None = None,
        gossip_engine: GossipEngine | None = None,
    ) -> None:
        """Create a new World in a stopped state, at tick zero.

        Args:
            clock: Clock to use. Defaults to a new ``Clock()``.
            scheduler: Scheduler to use. Defaults to a new ``Scheduler``
                bound to ``clock``. If you pass your own ``scheduler``,
                make sure it is bound to the same ``clock`` you pass here.
            agent_manager: AgentManager to use. Defaults to a new,
                empty ``AgentManager()``.
            event_bus: EventBus to use. Defaults to a new ``EventBus()``.
            memory_manager: MemoryManager to use. Defaults to a new,
                empty ``MemoryManager()``.
            conversation_engine: ConversationEngine to use. Defaults to a
                new one bound to ``memory_manager``. If you pass your own,
                make sure it is bound to the same ``memory_manager``.
            gossip_engine: GossipEngine to use. Defaults to a new one bound
                to ``agent_manager``, ``memory_manager``, and
                ``conversation_engine``. If you pass your own, make sure it
                is bound to the same instances.
        """
        self.is_running: bool = False
        self.tick_count: int = 0

        self.clock = clock if clock is not None else Clock()
        self.scheduler = scheduler if scheduler is not None else Scheduler(self.clock)
        self.agent_manager = agent_manager if agent_manager is not None else AgentManager()
        self.event_bus = event_bus if event_bus is not None else EventBus()
        self.memory_manager = memory_manager if memory_manager is not None else MemoryManager()
        self.conversation_engine = (
            conversation_engine
            if conversation_engine is not None
            else ConversationEngine(self.memory_manager)
        )
        self.gossip_engine = (
            gossip_engine
            if gossip_engine is not None
            else GossipEngine(self.agent_manager, self.memory_manager, self.conversation_engine)
        )

    def start(self) -> None:
        """Start the simulation and publish a ``WORLD_STARTED`` event.

        Idempotent: calling ``start()`` on an already-running world is a
        no-op (aside from a warning log).
        """
        if self.is_running:
            logger.warning("World.start() called but the world is already running.")
            return

        self.is_running = True
        logger.info("World started.")
        self.event_bus.publish(
            Event(event_type=EventType.WORLD_STARTED, timestamp=self.clock.current_time)
        )

    def stop(self) -> None:
        """Stop the simulation and publish a ``WORLD_STOPPED`` event.

        Idempotent for the same reason as ``start()``.
        """
        if not self.is_running:
            logger.warning("World.stop() called but the world is not running.")
            return

        self.is_running = False
        logger.info("World stopped at tick %d.", self.tick_count)
        self.event_bus.publish(
            Event(event_type=EventType.WORLD_STOPPED, timestamp=self.clock.current_time)
        )

    def tick(self) -> None:
        """Advance the simulation by exactly one tick.

        Does nothing if the world is not running. Otherwise increments
        ``tick_count`` and delegates to ``update()`` to run the tick
        lifecycle.
        """
        if not self.is_running:
            logger.warning("World.tick() called while the world is not running.")
            return

        self.tick_count += 1
        self.update()

    def update(self) -> None:
        """Execute the tick lifecycle for the current tick.

        Order:

        1. Advance the Clock.
        2. Execute due scheduled tasks.
        3. Update all agents.
        4. Run one gossip tick (post-movement).
        5. Publish a ``TICK`` event.
        """
        self.clock.advance()
        self.scheduler.run_due_tasks()
        self.agent_manager.update_all()
        self.gossip_engine.process_tick(self.clock.current_time)
        self.event_bus.publish(
            Event(
                event_type=EventType.TICK,
                timestamp=self.clock.current_time,
                payload={"tick_count": self.tick_count},
            )
        )
