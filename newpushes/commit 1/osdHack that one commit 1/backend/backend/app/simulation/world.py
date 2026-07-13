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

        self.narrative_events: list[dict] = []
        self.active_scene: str = "cafe"
        self.scene_step: int = 0

    def start(self) -> None:
        """Start the simulation and publish a ``WORLD_STARTED`` event."""
        if self.is_running:
            logger.warning("World.start() called but the world is already running.")
            return

        self.is_running = True
        logger.info("World started.")
        self.event_bus.publish(
            Event(event_type=EventType.WORLD_STARTED, timestamp=self.clock.current_time)
        )

        if self.scene_step == 0:
            for _ in range(3):
                self._process_scene_tick()

    def stop(self) -> None:
        """Stop the simulation and publish a ``WORLD_STOPPED`` event."""
        if not self.is_running:
            logger.warning("World.stop() called but the world is not running.")
            return

        self.is_running = False
        logger.info("World stopped at tick %d.", self.tick_count)
        self.event_bus.publish(
            Event(event_type=EventType.WORLD_STOPPED, timestamp=self.clock.current_time)
        )

    def tick(self) -> None:
        """Advance the simulation by exactly one tick."""
        if not self.is_running:
            logger.warning("World.tick() called while the world is not running.")
            return

        self.tick_count += 1
        self.update()

    def update(self) -> None:
        """Execute the tick lifecycle for the current tick.

        Order:
        1. Advance Clock.
        2. Execute scheduled tasks.
        3. Update agents.
        4. Gossip.
        5. Tick active scene.
        6. Publish Tick event.
        """
        self.clock.advance()
        self.scheduler.run_due_tasks()
        self.agent_manager.update_all()
        self.gossip_engine.process_tick(self.clock.current_time)

        self._process_scene_tick()

        self.event_bus.publish(
            Event(
                event_type=EventType.TICK,
                timestamp=self.clock.current_time,
                payload={"tick_count": self.tick_count},
            )
        )

    def _process_scene_tick(self) -> None:
        """Process the active scene step and generate a detailed novel-style event."""
        import uuid

        # Calculate day and time from clock.current_time (which is in seconds)
        day = int(self.clock.current_time // 86400) + 1
        hours = int((self.clock.current_time % 86400) // 3600)
        minutes = int((self.clock.current_time % 3600) // 60)
        time_str = f"{hours:02d}:{minutes:02d}"

        if self.active_scene == "cafe":
            # Check if agents have been influenced via memories
            bob_memories = self.memory_manager.get_memories("agent_2")
            is_bob_comforted = any("alright" in m.summary.lower() or "worry" in m.summary.lower() for m in bob_memories)

            carol_memories = self.memory_manager.get_memories("agent_3")
            is_carol_warned = any("danger" in m.summary.lower() or "caution" in m.summary.lower() for m in carol_memories)

            alice_memories = self.memory_manager.get_memories("agent_1")
            is_alice_suspicious = any("right" in m.summary.lower() or "unease" in m.summary.lower() for m in alice_memories)

            cafe_scripts = [
                {
                    "id": f"event_{self.tick_count}_0",
                    "day": day,
                    "time": time_str,
                    "location": "Café",
                    "type": "discovery",
                    "participants": ["Alice"],
                    "is_dialogue": False,
                    "narrative": "Alice settles into her corner table at the Café. Sunlight filters through the blinds, smelling of roasted beans and dust."
                },
                {
                    "id": f"event_{self.tick_count}_1",
                    "day": day,
                    "time": time_str,
                    "location": "Café",
                    "type": "social",
                    "participants": ["Alice"],
                    "is_dialogue": True,
                    "speaker": "Alice",
                    "narrative": '"Something about today feels off. An invisible weight hangs in the air."' if is_alice_suspicious else '"A peaceful start to the day. Let\'s hope it lasts."'
                },
                {
                    "id": f"event_{self.tick_count}_2",
                    "day": day,
                    "time": time_str,
                    "location": "Café",
                    "type": "social",
                    "participants": ["Bob"],
                    "is_dialogue": True,
                    "speaker": "Bob",
                    "narrative": '"Things will work out. I don\'t need to worry so much. But we must be observant."' if is_bob_comforted else '"The town is unsafe lately. Have you seen Carol? I don\'t know who we can trust anymore."'
                },
                {
                    "id": f"event_{self.tick_count}_3",
                    "day": day,
                    "time": time_str,
                    "location": "Café",
                    "type": "social",
                    "participants": ["Carol"],
                    "is_dialogue": True,
                    "speaker": "Carol",
                    "narrative": '"Something feels dangerous about this place. I have a bad feeling about what\'s coming. We should be very careful."' if is_carol_warned else '"I heard Emma found a crucial clue near the fountain. But Thomas is keeping secrets."'
                },
                {
                    "id": f"event_{self.tick_count}_4",
                    "day": day,
                    "time": time_str,
                    "location": "Café",
                    "type": "discovery",
                    "participants": ["Dave"],
                    "is_dialogue": False,
                    "narrative": "Dave, the town guard, patrols past the window, making notes in his logbook. The Café goes quiet."
                },
                {
                    "id": f"event_{self.tick_count}_5",
                    "day": day,
                    "time": time_str,
                    "location": "Café",
                    "type": "social",
                    "participants": ["Emma"],
                    "is_dialogue": True,
                    "speaker": "Emma",
                    "narrative": '"I know what you did near the spice stall, Thomas! You were there!"'
                },
                {
                    "id": f"event_{self.tick_count}_6",
                    "day": day,
                    "time": time_str,
                    "location": "Café",
                    "type": "social",
                    "participants": ["Thomas"],
                    "is_dialogue": True,
                    "speaker": "Thomas",
                    "narrative": '"I don\'t know what you are talking about. Leave me be."'
                },
                {
                    "id": f"event_{self.tick_count}_7",
                    "day": day,
                    "time": time_str,
                    "location": "Café",
                    "type": "social",
                    "participants": ["Carol"],
                    "is_dialogue": True,
                    "speaker": "Carol",
                    "narrative": '"If we gather enough evidence with collect, we can accuse the suspect and submit the case. Type court.exe to go to Court."'
                }
            ]

            script = cafe_scripts[self.scene_step % len(cafe_scripts)].copy()
            script["id"] = f"evt_{uuid.uuid4().hex[:12]}"
            self.narrative_events.append(script)
            self.scene_step += 1

        elif self.active_scene == "court":
            case_file = getattr(self, "case_file", None)
            court_engine = getattr(self, "court_engine", None)

            evidence_str = ""
            if case_file:
                evidence_list = case_file.list_evidence()
                if evidence_list:
                    evidence_str = ", ".join(f"[{e.memory.summary}]" for e in evidence_list)
                else:
                    evidence_str = "(No evidence collected)"

            verdict_str = "No verdict evaluated yet."
            if case_file and court_engine:
                verdict = court_engine.evaluate(case_file)
                if verdict.success:
                    verdict_str = f"CONVICTED. The Court finds {verdict.culprit_id} GUILTY based on sufficient evidence."
                else:
                    verdict_str = f"ACQUITTED. The Court finds insufficient evidence to convict {verdict.culprit_id}."

            court_scripts = [
                {
                    "id": f"event_{self.tick_count}_0",
                    "day": day,
                    "time": time_str,
                    "location": "Court",
                    "type": "court",
                    "participants": ["Carol"],
                    "is_dialogue": False,
                    "narrative": "The heavy doors of the Court swing open. Judge Carol takes the bench and strikes her gavel."
                },
                {
                    "id": f"event_{self.tick_count}_1",
                    "day": day,
                    "time": time_str,
                    "location": "Court",
                    "type": "court",
                    "participants": ["Carol"],
                    "is_dialogue": True,
                    "speaker": "Judge Carol",
                    "narrative": '"This court is now in session. Bring in the suspect and present the case findings."'
                },
                {
                    "id": f"event_{self.tick_count}_2",
                    "day": day,
                    "time": time_str,
                    "location": "Court",
                    "type": "court",
                    "participants": ["Dave"],
                    "is_dialogue": True,
                    "speaker": "Prosecutor Dave",
                    "narrative": f'"Your Honor, I present the compiled case record. Active evidence: {evidence_str}."'
                },
                {
                    "id": f"event_{self.tick_count}_3",
                    "day": day,
                    "time": time_str,
                    "location": "Court",
                    "type": "court",
                    "participants": ["Dave"],
                    "is_dialogue": True,
                    "speaker": "Prosecutor Dave",
                    "narrative": '"Suspect, explain your presence at the market at the time of the silk theft!"'
                },
                {
                    "id": f"event_{self.tick_count}_4",
                    "day": day,
                    "time": time_str,
                    "location": "Court",
                    "type": "court",
                    "participants": ["Carol"],
                    "is_dialogue": True,
                    "speaker": "Judge Carol",
                    "narrative": f'"Having reviewed the case file record, the Court hereby renders its final verdict: {verdict_str}"'
                },
                {
                    "id": f"event_{self.tick_count}_5",
                    "day": day,
                    "time": time_str,
                    "location": "Court",
                    "type": "court",
                    "participants": ["Carol"],
                    "is_dialogue": False,
                    "narrative": "Judge Carol strikes her gavel again. The session is closed. Spectators filter out into the town."
                }
            ]

            script = court_scripts[self.scene_step % len(court_scripts)].copy()
            script["id"] = f"evt_{uuid.uuid4().hex[:12]}"
            self.narrative_events.append(script)
            self.scene_step += 1

    def run_full_cafe_scene(self) -> str:
        """Run all Cafe scene steps and return the compiled novel dialogue transcript."""
        self.active_scene = "cafe"
        self.scene_step = 0

        lines = []
        for _ in range(8):
            self._process_scene_tick()
            evt = self.narrative_events[-1]
            if evt.get("is_dialogue", False):
                lines.append(f"[{evt['time']}] @{evt['speaker']}: {evt['narrative']}")
            else:
                lines.append(f"[{evt['time']}] * {evt['narrative']} *")

        return "\n\n".join(lines)

    def run_full_court_scene(self) -> str:
        """Run all Court scene steps and return the compiled novel dialogue transcript."""
        self.active_scene = "court"
        self.scene_step = 0

        lines = []
        for _ in range(6):
            self._process_scene_tick()
            evt = self.narrative_events[-1]
            if evt.get("is_dialogue", False):
                lines.append(f"[{evt['time']}] @{evt['speaker']}: {evt['narrative']}")
            else:
                lines.append(f"[{evt['time']}] * {evt['narrative']} *")

        return "\n\n".join(lines)
