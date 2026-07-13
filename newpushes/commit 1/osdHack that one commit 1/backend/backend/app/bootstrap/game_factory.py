"""GameFactory: the single place where the full EchoCity object graph is wired.

This module contains no gameplay logic. It only constructs subsystems in
dependency order and returns them as one object. Any future CLI, demo
script, or test that needs a fully wired EchoCity world should call
GameFactory.build() instead of constructing subsystems manually.
"""

from dataclasses import dataclass

from app.agents.agent import Agent
from app.agents.agent_state import AgentState
from app.court.case_file import CaseFile
from app.court.court_engine import CourtEngine
from app.court.evidence_manager import EvidenceManager
from app.crime.crime_engine import CrimeEngine
from app.higher_self.higher_self_engine import HigherSelfEngine
from app.investigation.investigation_service import InvestigationService
from app.shell.shell import Shell
from app.simulation.location import Location
from app.simulation.location_manager import LocationManager
from app.simulation.location_type import LocationType
from app.simulation.world import World

_CAFE_ID = "cafe"
_COURT_ID = "court"
_INITIAL_GOSSIP_TICKS = 5

_DEMO_AGENTS = [
    ("agent_1", "Alice"),
    ("agent_2", "Bob"),
    ("agent_3", "Carol"),
    ("agent_4", "Dave"),
    ("agent_5", "Emma"),
    ("agent_6", "Frank"),
    ("agent_7", "Grace"),
    ("agent_8", "Henry"),
]


@dataclass(frozen=True)
class Game:
    """Application-level services exposed to entrypoints, future frontends,
    and Higher Self operations.

    Internal wiring (CrimeEngine, EvidenceManager, CaseFile, CourtEngine,
    InvestigationService, ConversationEngine, GossipEngine) stays inside
    the factory unless a concrete caller needs direct access.

    Attributes:
        world: Root simulation object.
        shell: The interactive EchoShell, ready to accept commands.
        location_manager: Registry of all Locations.
    """

    world: World
    shell: Shell
    location_manager: LocationManager


class GameFactory:
    """Builds a complete, playable EchoCity object graph.

    The only place in the codebase where subsystem constructors are
    manually wired together.
    """

    @staticmethod
    def build() -> Game:
        """Construct and return a fully initialized demo Game.

        Registers the Cafe and Court locations, creates the demo NPCs,
        seeds the crime and witness memories, and assembles the shell.

        Returns:
            A ready-to-play Game.
        """
        world = World()

        location_manager = LocationManager()
        cafe = Location(id=_CAFE_ID, name="Cafe", type=LocationType.CAFE)
        court = Location(id=_COURT_ID, name="Court", type=LocationType.COURT)
        location_manager.register_location(cafe)
        location_manager.register_location(court)

        for agent_id, name in _DEMO_AGENTS:
            world.agent_manager.register(
                Agent(
                    agent_id=agent_id,
                    name=name,
                    state=AgentState.IDLE,
                    goal=None,
                    location=cafe,
                )
            )

        crime_engine = CrimeEngine(world.memory_manager)
        crime_engine.create_crime()
        crime_engine.seed_memories()

        # Deliberately calling gossip_engine directly rather than
        # world.update()/world.tick(): pre-game seeding should not
        # advance the Clock, run the Scheduler, or publish TICK events
        # before the player's session has actually started.
        for _ in range(_INITIAL_GOSSIP_TICKS):
            world.gossip_engine.process_tick(world.clock.current_time)

        evidence_manager = EvidenceManager()
        case_file = CaseFile()
        court_engine = CourtEngine(crime_engine)
        investigation_service = InvestigationService(world.agent_manager, world.memory_manager)
        world.case_file = case_file
        world.court_engine = court_engine

        higher_self_engine = HigherSelfEngine(world.memory_manager, world.agent_manager)
        shell = Shell(
            world, investigation_service, evidence_manager, case_file, court_engine, higher_self_engine
        )

        return Game(world=world, shell=shell, location_manager=location_manager)
