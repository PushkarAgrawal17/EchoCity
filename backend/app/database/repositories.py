"""Repositories for saving and loading simulation state from SQLite."""

import logging
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.agent import Agent, Relationship
from app.agents.agent_state import AgentState
from app.conversation.conversation import Conversation
from app.database.models import (
    AgentModel,
    DiaryModel,
    LocationModel,
    MemoryModel,
    NarrativeEventModel,
    RelationshipModel,
    WorldStateModel,
)
from app.memory.memory import Memory
from app.memory.memory_type import MemoryType
from app.simulation.location import Location
from app.simulation.location_type import LocationType
from app.simulation.world import World

logger = logging.getLogger(__name__)


class SimulationRepository:
    """Manages transactional database operations for the simulation World."""

    def __init__(self, session_maker: any) -> None:
        """Create a SimulationRepository.

        Args:
            session_maker: An async_sessionmaker factory.
        """
        self.session_maker = session_maker

    async def save_world(self, world: World) -> None:
        """Serialize the complete in-memory World state into SQLite.

        Saves clock frames, agents, inventories, needs, relationships,
        memories, diaries, and narrative event history in one transaction.

        Args:
            world: The World instance to save.
        """
        logger.info("Saving world state to SQLite database...")
        async with self.session_maker() as session:
            async with session.begin():
                # 1. Save World State
                world_state_query = select(WorldStateModel).where(WorldStateModel.id == 1)
                result = await session.execute(world_state_query)
                state_model = result.scalar_one_or_none()

                if not state_model:
                    state_model = WorldStateModel(id=1)
                    session.add(state_model)

                state_model.tick_count = world.tick_count
                state_model.current_time = world.clock.current_time
                state_model.is_running = world.is_running
                state_model.active_scene = world.active_scene
                state_model.scene_step = world.scene_step

                # 2. Save Locations
                for loc in world.location_manager.list_locations():
                    loc_query = select(LocationModel).where(LocationModel.id == loc.id)
                    loc_res = await session.execute(loc_query)
                    loc_model = loc_res.scalar_one_or_none()

                    if not loc_model:
                        loc_model = LocationModel(id=loc.id)
                        session.add(loc_model)

                    loc_model.name = loc.name
                    loc_model.type = loc.type.value

                # 3. Clear existing relations/memories/diaries/narratives to prevent duplicate/orphan rows
                await session.execute(delete(RelationshipModel))
                await session.execute(delete(MemoryModel))
                await session.execute(delete(DiaryModel))
                await session.execute(delete(NarrativeEventModel))

                # 4. Save Agents, Relationships, Memories, and Diaries
                for agent in world.agent_manager:
                    agent_query = select(AgentModel).where(AgentModel.agent_id == agent.agent_id)
                    agent_res = await session.execute(agent_query)
                    agent_model = agent_res.scalar_one_or_none()

                    if not agent_model:
                        agent_model = AgentModel(agent_id=agent.agent_id)
                        session.add(agent_model)

                    agent_model.name = agent.name
                    agent_model.state = agent.state.name
                    agent_model.goal = agent.goal
                    agent_model.location_id = agent.location.id if agent.location else None
                    agent_model.age = agent.age
                    agent_model.occupation = agent.occupation
                    agent_model.home = agent.home
                    agent_model.personality = agent.personality
                    agent_model.speech_style = agent.speech_style
                    agent_model.habits = agent.habits
                    agent_model.inventory = agent.inventory
                    agent_model.secrets = agent.secrets
                    agent_model.beliefs = agent.beliefs
                    agent_model.stress = agent.stress
                    agent_model.suspicion = agent.suspicion
                    agent_model.energy = agent.energy
                    agent_model.confidence = agent.confidence
                    agent_model.emotion = agent.emotion

                    # Save relationships
                    for target_id, rel in agent.relationships.items():
                        rel_model = RelationshipModel(
                            agent_id=agent.agent_id,
                            target_agent_id=target_id,
                            trust=rel.trust,
                            friendship=rel.friendship,
                            respect=rel.respect,
                            fear=rel.fear,
                            romantic=rel.romantic,
                            hidden_opinion=rel.hidden_opinion,
                            shared_memory=rel.shared_memory,
                        )
                        session.add(rel_model)

                    # Save memories
                    memories = world.memory_manager.get_memories(agent.agent_id)
                    for mem in memories:
                        mem_model = MemoryModel(
                            memory_id=mem.id,
                            agent_id=agent.agent_id,
                            summary=mem.summary,
                            type=mem.type.value,
                            source=mem.source,
                            timestamp=mem.timestamp,
                            confidence=mem.confidence,
                            shared=mem.shared,
                            subject_id=mem.subject_id,
                        )
                        session.add(mem_model)

                    # Save diaries
                    diaries = world.diaries.get(agent.agent_id, [])
                    for diary in diaries:
                        diary_model = DiaryModel(
                            agent_id=agent.agent_id,
                            day=diary["day"],
                            label=diary["label"],
                            text=diary["text"],
                        )
                        session.add(diary_model)

                # 5. Save Narrative Events
                for event in world.narrative_events:
                    event_model = NarrativeEventModel(
                        id=event["id"],
                        day=event["day"],
                        time=event["time"],
                        location=event["location"],
                        type=event["type"],
                        participants=event["participants"],
                        is_dialogue=event.get("is_dialogue", False),
                        speaker=event.get("speaker"),
                        narrative=event["narrative"],
                        status=event.get("status", "completed"),
                    )
                    session.add(event_model)

        logger.info("World state successfully saved to SQLite.")

    async def load_world(self, world: World) -> bool:
        """Deserialize database state back into the active in-memory World.

        Updates clock ticks, agent needs, goals, memories, relationship links,
        diaries, and narrative events.

        Args:
            world: The World instance to update.

        Returns:
            True if state was loaded successfully, False if database is empty.
        """
        logger.info("Loading world state from SQLite database...")
        async with self.session_maker() as session:
            # 1. Verify if world state exists
            state_query = select(WorldStateModel).where(WorldStateModel.id == 1)
            result = await session.execute(state_query)
            state_model = result.scalar_one_or_none()

            if not state_model:
                logger.warning("No saved world state found in SQLite.")
                return False

            # Restore global variables
            world.tick_count = state_model.tick_count
            world.clock._tick_count = state_model.tick_count # sync clock ticks
            world.is_running = state_model.is_running
            world.active_scene = state_model.active_scene
            world.scene_step = state_model.scene_step

            # 2. Load Locations
            loc_query = select(LocationModel)
            loc_res = await session.execute(loc_query)
            for loc_model in loc_res.scalars():
                # Re-register if not already present
                existing = world.location_manager.get(loc_model.id)
                if not existing:
                    world.location_manager.register_location(
                        Location(
                            id=loc_model.id,
                            name=loc_model.name,
                            type=LocationType(loc_model.type),
                        )
                    )

            # 3. Load Agents
            agent_query = select(AgentModel)
            agent_res = await session.execute(agent_query)
            agents = agent_res.scalars().all()

            # Clear current agents from manager
            for existing_agent in list(world.agent_manager):
                world.agent_manager.remove(existing_agent.agent_id)

            for a_model in agents:
                agent = Agent(
                    agent_id=a_model.agent_id,
                    name=a_model.name,
                    state=AgentState[a_model.state],
                    goal=a_model.goal,
                    location=world.location_manager.get(a_model.location_id) if a_model.location_id else None,
                    age=a_model.age,
                    occupation=a_model.occupation,
                    home=a_model.home,
                    personality=a_model.personality,
                    speech_style=a_model.speech_style,
                    habits=a_model.habits,
                    inventory=a_model.inventory,
                    secrets=a_model.secrets,
                    beliefs=a_model.beliefs,
                    stress=a_model.stress,
                    suspicion=a_model.suspicion,
                    energy=a_model.energy,
                    confidence=a_model.confidence,
                    emotion=a_model.emotion,
                )
                # Schedules are loaded statically in GameFactory but restore just in case
                from app.bootstrap.game_factory import _AGENT_SCHEDULES
                agent.daily_schedule = _AGENT_SCHEDULES.get(a_model.agent_id, {})
                world.agent_manager.register(agent)

            # 4. Load Relationships
            rel_query = select(RelationshipModel)
            rel_res = await session.execute(rel_query)
            for r_model in rel_res.scalars():
                agent = world.agent_manager.get(r_model.agent_id)
                if agent:
                    agent.relationships[r_model.target_agent_id] = Relationship(
                        trust=r_model.trust,
                        friendship=r_model.friendship,
                        respect=r_model.respect,
                        fear=r_model.fear,
                        romantic=r_model.romantic,
                        hidden_opinion=r_model.hidden_opinion,
                        shared_memory=r_model.shared_memory,
                    )

            # 5. Load Memories
            # Clear memory manager first
            world.memory_manager._memories.clear()
            mem_query = select(MemoryModel)
            mem_res = await session.execute(mem_query)
            for m_model in mem_res.scalars():
                memory_obj = Memory(
                    id=m_model.memory_id,
                    summary=m_model.summary,
                    type=MemoryType(m_model.type),
                    source=m_model.source,
                    timestamp=m_model.timestamp,
                    confidence=m_model.confidence,
                    shared=m_model.shared,
                    subject_id=m_model.subject_id,
                )
                world.memory_manager.add_memory(m_model.agent_id, memory_obj)

            # 6. Load Diaries
            world.diaries.clear()
            diary_query = select(DiaryModel)
            diary_res = await session.execute(diary_query)
            for d_model in diary_res.scalars():
                entry = {
                    "day": d_model.day,
                    "label": d_model.label,
                    "text": d_model.text,
                }
                world.diaries.setdefault(d_model.agent_id, []).append(entry)

            # 7. Load Narrative Events
            world.narrative_events.clear()
            event_query = select(NarrativeEventModel).order_by(NarrativeEventModel.day, NarrativeEventModel.time)
            event_res = await session.execute(event_query)
            for e_model in event_res.scalars():
                event = {
                    "id": e_model.id,
                    "day": e_model.day,
                    "time": e_model.time,
                    "location": e_model.location,
                    "type": e_model.type,
                    "participants": e_model.participants,
                    "is_dialogue": e_model.is_dialogue,
                    "speaker": e_model.speaker,
                    "narrative": e_model.narrative,
                    "status": e_model.status,
                }
                world.narrative_events.append(event)

            logger.info("World state successfully loaded from SQLite database.")
            return True
