"""GameFactory: the single place where the full EchoCity object graph is wired.

This module contains no gameplay logic. It only constructs subsystems in
dependency order and returns them as one object.
"""

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from app.agents.agent import Agent, Relationship
from app.agents.agent_state import AgentState
from app.court.case_file import CaseFile
from app.court.court_engine import CourtEngine
from app.court.evidence_manager import EvidenceManager
from app.crime.crime_engine import CrimeEngine
from app.higher_self.higher_self_engine import HigherSelfEngine
from app.investigation.investigation_service import InvestigationService
from app.memory.memory import Memory
from app.memory.memory_type import MemoryType
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

# Detailed schedules for the 8 real agents matching the NPC Bible
_AGENT_SCHEDULES = {
    "marcus_hale": {
        6: ("Reviewing filings", "apartment_building", AgentState.WORKING),
        7: ("Walking to Court", "court", AgentState.WALKING),
        8: ("Reviewing docket in chambers", "court", AgentState.WORKING),
        9: ("Presiding over court", "court", AgentState.WORKING),
        12: ("Having lunch", "cafe", AgentState.IDLE),
        13: ("Presiding over court", "court", AgentState.WORKING),
        16: ("Chamber work", "court", AgentState.WORKING),
        17: ("Walking in the Park", "park", AgentState.IDLE),
        18: ("Having dinner", "apartment_building", AgentState.IDLE),
        19: ("Reading case law", "apartment_building", AgentState.WORKING),
        21: ("Writing letter", "apartment_building", AgentState.IDLE),
        22: ("Sleeping in armchair", "apartment_building", AgentState.SLEEPING),
        23: ("Sleeping", "apartment_building", AgentState.SLEEPING),
    },
    "ethan_cross": {
        6: ("Running his loop", "park", AgentState.WALKING),
        7: ("Checking reports", "apartment_building", AgentState.IDLE),
        8: ("Attending briefing", "police_station", AgentState.WORKING),
        9: ("Conducting interviews", "park", AgentState.WORKING),
        12: ("Having lunch", "cafe", AgentState.IDLE),
        13: ("Following up leads", "cafe", AgentState.WORKING),
        16: ("Reviewing notes", "police_station", AgentState.WORKING),
        18: ("Thinking on roof", "police_station", AgentState.IDLE),
        19: ("Having dinner", "apartment_building", AgentState.IDLE),
        20: ("At Cafe/Home", "apartment_building", AgentState.IDLE),
        21: ("Reviewing notes", "apartment_building", AgentState.WORKING),
        23: ("Sleeping", "apartment_building", AgentState.SLEEPING),
    },
    "ava_morgan": {
        6: ("Checking gossip", "apartment_building", AgentState.IDLE),
        7: ("Having morning coffee", "cafe", AgentState.IDLE),
        8: ("Planning leads", "apartment_building", AgentState.WORKING),
        9: ("Conducting interviews", "cafe", AgentState.WORKING),
        12: ("Writing article", "cafe", AgentState.WORKING),
        14: ("Chasing leads", "bank", AgentState.WALKING),
        17: ("Writing article", "cafe", AgentState.WORKING),
        19: ("Having dinner", "apartment_building", AgentState.IDLE),
        20: ("Reviewing recordings", "apartment_building", AgentState.WORKING),
        22: ("Reviewing notes", "apartment_building", AgentState.WORKING),
        23: ("Sleeping", "apartment_building", AgentState.SLEEPING),
    },
    "noah_reed": {
        6: ("Rehearsing talking points", "apartment_building", AgentState.IDLE),
        7: ("Dressing and having tea", "apartment_building", AgentState.IDLE),
        8: ("Checking vault", "bank", AgentState.WORKING),
        9: ("Managing bank", "bank", AgentState.WORKING),
        12: ("Having lunch/reviewing ledgers", "bank", AgentState.WORKING),
        14: ("Attending meetings", "bank", AgentState.WORKING),
        17: ("Closing out the day", "bank", AgentState.WORKING),
        18: ("Walking home", "apartment_building", AgentState.WALKING),
        19: ("Having dinner", "apartment_building", AgentState.IDLE),
        20: ("Drinking quietly", "apartment_building", AgentState.IDLE),
        21: ("Reviewing personal ledger", "apartment_building", AgentState.WORKING),
        23: ("Sleeping", "apartment_building", AgentState.SLEEPING),
    },
    "emma_brooks": {
        6: ("Grading papers", "apartment_building", AgentState.WORKING),
        7: ("Walking to school", "school", AgentState.WALKING),
        8: ("Homeroom supervision", "school", AgentState.WORKING),
        9: ("Teaching classes", "school", AgentState.WORKING),
        12: ("Having lunch", "school", AgentState.WORKING),
        13: ("Teaching classes", "school", AgentState.WORKING),
        15: ("Grading papers", "school", AgentState.WORKING),
        17: ("Walking in the Park", "park", AgentState.IDLE),
        18: ("Having dinner", "apartment_building", AgentState.IDLE),
        19: ("Planning lessons", "apartment_building", AgentState.WORKING),
        20: ("Reading", "apartment_building", AgentState.IDLE),
        21: ("Writing in journal", "apartment_building", AgentState.WORKING),
        22: ("Sleeping", "apartment_building", AgentState.SLEEPING),
    },
    "liam_carter": {
        6: ("Reviewing logs", "apartment_building", AgentState.WORKING),
        7: ("Hospital rounds", "hospital", AgentState.WORKING),
        8: ("Treating patients", "hospital", AgentState.WORKING),
        12: ("Having lunch", "hospital", AgentState.IDLE),
        13: ("Treating patients", "hospital", AgentState.WORKING),
        16: ("Tending rooftop garden", "hospital", AgentState.IDLE),
        18: ("Having dinner", "cafe", AgentState.IDLE),
        19: ("Hospital rounds", "hospital", AgentState.WORKING),
        20: ("Reading medical journals", "apartment_building", AgentState.WORKING),
        21: ("Writing letter", "apartment_building", AgentState.IDLE),
        22: ("Sleeping", "apartment_building", AgentState.SLEEPING),
    },
    "sophia_bennett": {
        6: ("Baking pastries", "cafe", AgentState.WORKING),
        7: ("Serving customers", "cafe", AgentState.WORKING),
        8: ("Serving customers", "cafe", AgentState.WORKING),
        12: ("Serving customers", "cafe", AgentState.WORKING),
        14: ("Restocking Cafe", "cafe", AgentState.WORKING),
        17: ("Serving customers", "cafe", AgentState.WORKING),
        19: ("Serving customers", "cafe", AgentState.WORKING),
        21: ("Cleaning Cafe", "cafe", AgentState.WORKING),
        22: ("Reading", "apartment_building", AgentState.IDLE),
        23: ("Sleeping", "apartment_building", AgentState.SLEEPING),
    },
    "victor_kane": {
        6: ("Checking on Timmy", "apartment_building", AgentState.IDLE),
        7: ("Walking Timmy to school", "school", AgentState.WALKING),
        8: ("Working at Garage", "garage", AgentState.WORKING),
        12: ("Having lunch", "garage", AgentState.IDLE),
        13: ("Working at Garage", "garage", AgentState.WORKING),
        17: ("Closing Garage", "garage", AgentState.WORKING),
        18: ("Walking home/Having dinner", "apartment_building", AgentState.WALKING),
        19: ("Helping Timmy", "apartment_building", AgentState.IDLE),
        21: ("Thinking in quiet", "apartment_building", AgentState.IDLE),
        22: ("Sleeping", "apartment_building", AgentState.SLEEPING),
    }
}

_NAME_TO_ID = {
    "Marcus Hale": "marcus_hale",
    "Ethan Cross": "ethan_cross",
    "Ava Morgan": "ava_morgan",
    "Noah Reed": "noah_reed",
    "Emma Brooks": "emma_brooks",
    "Liam Carter": "liam_carter",
    "Sophia Bennett": "sophia_bennett",
    "Victor Kane": "victor_kane"
}


@dataclass(frozen=True)
class Game:
    """Application-level services exposed to entrypoints."""
    world: World
    shell: Shell
    location_manager: LocationManager


class GameFactory:
    """Builds a complete, playable EchoCity object graph."""

    @staticmethod
    def build(demo: bool = True) -> Game:
        """Construct and return a fully initialized Game.

        Args:
            demo: If True, boots up the mock world to keep unit tests passing.
                If False, loads the real EchoCity NPC Bible world.

        Returns:
            A ready-to-play Game.
        """
        location_manager = LocationManager()
        world = World(location_manager=location_manager, demo=demo)

        if demo:
            # Booting mock/demo world
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

            for _ in range(_INITIAL_GOSSIP_TICKS):
                world.gossip_engine.process_tick(world.clock.current_time)
        else:
            # Register the 9 real locations
            locations_data = [
                ("court", "Court", LocationType.COURT),
                ("police_station", "Police Station", LocationType.POLICE_STATION),
                ("cafe", "Cafe", LocationType.CAFE),
                ("bank", "Bank", LocationType.BANK),
                ("hospital", "Hospital", LocationType.HOSPITAL),
                ("school", "School", LocationType.SCHOOL),
                ("garage", "Garage", LocationType.GARAGE),
                ("apartment_building", "Apartment Building", LocationType.APARTMENT_BUILDING),
                ("park", "Park", LocationType.PARK),
            ]
            for loc_id, name, loc_type in locations_data:
                location_manager.register_location(Location(id=loc_id, name=name, type=loc_type))

            # Load agents and details from JSON
            json_path = Path(__file__).parent / "seeded_agents.json"
            with open(json_path, encoding="utf-8") as f:
                agents_data = json.load(f)

            # 1. Register Agent objects
            for citizen_data in agents_data:
                info = citizen_data["citizen_info"]
                agent_id = info["id"]
                
                # Starting location is Cafe for Sophia, Apartment Building for everyone else
                start_loc_id = "cafe" if agent_id == "sophia_bennett" else "apartment_building"
                
                agent = Agent(
                    agent_id=agent_id,
                    name=info["name"],
                    state=AgentState.IDLE,
                    goal=info["current_state"]["goal"],
                    location=location_manager.get(start_loc_id),
                    age=info["age"],
                    occupation=info["occupation"],
                    home=info["home"],
                    personality=info["personality"],
                    speech_style=info["speech_style"],
                    habits=info["habits"],
                    inventory=info["inventory"],
                    secrets=info["secrets"],
                    beliefs=info["beliefs"],
                    stress=info["current_state"]["stress"],
                    suspicion=info["current_state"]["suspicion"],
                    energy=info["current_state"]["energy"],
                    confidence=info["current_state"]["confidence"],
                    emotion=info["current_state"]["emotion"]
                )
                agent.daily_schedule = _AGENT_SCHEDULES.get(agent_id, {})
                world.agent_manager.register(agent)

            # 2. Seed Relationship Networks
            for citizen_data in agents_data:
                agent_id = citizen_data["citizen_info"]["id"]
                agent = world.agent_manager.get(agent_id)
                for rel in citizen_data["relationships"]:
                    target_id = _NAME_TO_ID.get(rel["with"])
                    if target_id and agent:
                        agent.relationships[target_id] = Relationship(
                            trust=rel["trust"],
                            friendship=rel["friendship"],
                            respect=rel["respect"],
                            fear=rel["fear"],
                            romantic=rel["romantic"],
                            hidden_opinion=rel["hidden_opinion"],
                            shared_memory=rel["shared_memory"]
                        )

            # 3. Seed Memories
            def parse_day_to_seconds(ts_str: str) -> float:
                match = re.search(r'Day\s+(-?\d+)', ts_str)
                if match:
                    day = int(match.group(1))
                    return float(day * 86400)
                return 0.0

            for citizen_data in agents_data:
                agent_id = citizen_data["citizen_info"]["id"]
                for mem in citizen_data["memories"]:
                    # Categorize memory type
                    mem_type = MemoryType.PERSONAL
                    if "secret" in mem["tags"] or "family" in mem["tags"]:
                        mem_type = MemoryType.PERSONAL
                    elif "suspicion" in mem["tags"] or "case" in mem["tags"]:
                        mem_type = MemoryType.WITNESS
                    
                    memory_obj = Memory(
                        id=mem["id"],
                        summary=mem["summary"],
                        type=mem_type,
                        source="self",
                        timestamp=parse_day_to_seconds(mem["timestamp_str"]),
                        confidence=1.0,
                        subject_id=None
                    )
                    world.memory_manager.add_memory(agent_id, memory_obj)

            # 4. Attach Diaries list to World for serialization later
            world.diaries = {}
            for citizen_data in agents_data:
                agent_id = citizen_data["citizen_info"]["id"]
                world.diaries[agent_id] = citizen_data["diaries"]

        # Subsystems setup
        evidence_manager = EvidenceManager()
        case_file = CaseFile()
        
        # If demo, use mock crime_engine
        if demo:
            crime_engine = CrimeEngine(world.memory_manager)
            court_engine = CourtEngine(crime_engine)
        else:
            # We don't have mock crime_engine in real game, we just use a basic CourtEngine
            # or mock logic since the actual Court trial is driven via AI scene ticks
            court_engine = CourtEngine(None)
            
        investigation_service = InvestigationService(world.agent_manager, world.memory_manager)
        world.case_file = case_file
        world.court_engine = court_engine

        higher_self_engine = HigherSelfEngine(world.memory_manager, world.agent_manager)
        shell = Shell(
            world, investigation_service, evidence_manager, case_file, court_engine, higher_self_engine
        )

        return Game(world=world, shell=shell, location_manager=location_manager)
