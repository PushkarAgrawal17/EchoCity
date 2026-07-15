"""BrainService: orchestrates local AI prompt construction, inference, and world updates."""

import logging
import uuid
from typing import Any
from app.agents.agent import Relationship
from app.api.websocket import manager as ws_manager
from app.conversation.conversation import Conversation
from app.events.event import Event
from app.events.event_type import EventType
from app.llm.client import OllamaClient
from app.llm.llm_service import LLMService
from app.llm.context_builder import ContextBuilder
from app.memory.memory_type import MemoryType
from app.simulation.world import World

logger = logging.getLogger(__name__)


class BrainService:
    """Orchestrates local AI inference and handles state synchronization.

    Converts raw LLM results into structured updates: validates JSON schemas,
    updates agent goals and SQLite tables, inserts cognitive memories, shifts
    relationship metrics, publishes event notifications, and triggers WebSockets.
    
    CRITICAL: Only the LLM Service interacts with Ollama. BrainService delegates to it.
    """

    def __init__(self, world: World, client: OllamaClient) -> None:
        """Create a BrainService.

        Args:
            world: Reference to the root World object.
            client: The local Ollama client instance.
        """
        self.world = world
        self.client = client
        self.llm_service = LLMService(self.client)

    async def generate_gossip(self, conversation: Conversation, placeholder_id: str) -> None:
        """Asynchronously generate and apply a gossip dialogue between speaker and listener.

        Args:
            conversation: The gossip Conversation record.
            placeholder_id: ID of the placeholder event to update.
        """
        speaker = self.world.agent_manager.get(conversation.speaker_id)
        listener = self.world.agent_manager.get(conversation.listener_id)
        if not speaker or not listener:
            return

        memory = self.world.memory_manager.get_memory(conversation.speaker_id, conversation.memory_id)
        location_name = speaker.location.name if speaker.location else "Cafe"

        # 1. Build token-minimized LLM Context
        ctx = ContextBuilder.build(
            reasoning_task="Conversation",
            current_agent=speaker,
            nearby_agents=[listener],
            current_scene=location_name,
            relevant_memories=[memory] if memory else [],
        )

        # 2. Query LLM service (LLM Service handles the actual Ollama network call)
        res = await self.llm_service.reason("Conversation", ctx)

        # 3. Validate JSON payload
        dialogue = res.get("dialogue")
        if not dialogue or not isinstance(dialogue, str):
            logger.warning("BrainService: Invalid JSON response for Gossip conversation, using fallback.")
            dialogue = f"{speaker.name} whispers to {listener.name}: '{memory.summary if memory else 'something interesting'}'."

        # 4. Update SQLite (Narrative placeholder event modification)
        for event in self.world.narrative_events:
            if event.get("id") == placeholder_id:
                event["narrative"] = dialogue
                event["status"] = "completed"
                break

        # 5. Create new cognitive memory for the listener
        await self.world.memory_engine.perceive_event(
            agent_id=listener.agent_id,
            agent_name=listener.name,
            agent_occupation=listener.occupation,
            raw_event_description=f"{speaker.name} gossiped: '{dialogue}'",
            location_name=location_name,
            timestamp=self.world.clock.current_time,
            source=speaker.agent_id,
            memory_type=MemoryType.PERSONAL
        )

        # 6. Update Relationships (shift trust metrics based on conversation keywords)
        trust_change = 0.02
        dialogue_lower = dialogue.lower()
        if any(w in dialogue_lower for w in ["stole", "liar", "secret", "theft", "debt"]):
            trust_change = -0.05
        elif any(w in dialogue_lower for w in ["agree", "help", "good", "friend"]):
            trust_change = 0.04

        rel = speaker.relationships.setdefault(
            listener.agent_id, 
            Relationship(trust=0.5, friendship=0.5, respect=0.5, fear=0.0, romantic=0.0, hidden_opinion="", shared_memory="")
        )
        rel.trust = max(0.0, min(1.0, rel.trust + trust_change))

        # 7. Generate new events (Publish Rumor Spread to EventBus)
        self.world.event_bus.publish(
            Event(
                event_type=EventType.RUMOR_SPREAD,
                timestamp=self.world.clock.current_time,
                payload={
                    "speaker_id": speaker.agent_id,
                    "listener_id": listener.agent_id,
                    "dialogue": dialogue
                }
            )
        )

        # 8. Trigger Frontend Updates over WebSocket
        await ws_manager.broadcast({
            "type": "NARRATIVE_EVENT_COMPLETED",
            "payload": {
                "event_id": placeholder_id,
                "narrative": dialogue,
                "status": "completed"
            }
        })

    async def generate_scene(self, location_id: str, placeholder_id: str) -> None:
        """Generate and apply a detailed novel-style scene narrative of agents at a location.

        Args:
            location_id: ID of the location to observe.
            placeholder_id: ID of the placeholder event to update.
        """
        location = self.world.location_manager.get(location_id)
        if not location:
            return

        co_located = [
            a for a in self.world.agent_manager
            if a.location is not None and a.location.id == location_id
        ]
        if not co_located:
            return

        # 1. Build token-minimized LLM Context
        ctx = ContextBuilder.build(
            reasoning_task="Higher Self Reasoning",
            current_agent=co_located[0] if co_located else None,
            nearby_agents=co_located[1:] if len(co_located) > 1 else [],
            relationships=co_located[0].relationships if co_located else {},
            current_scene=location,
            player_influence={"type": "Observation", "details": f"Narrating physical location scene for agents co-located at the {location.name}."}
        )

        # 2. Query LLM service
        res = await self.llm_service.reason("Higher Self Reasoning", ctx)

        # 3. Validate JSON payload
        narrative = res.get("narrative")
        if not narrative or not isinstance(narrative, str):
            logger.warning("BrainService: Invalid JSON response for Scene narrative, using fallback.")
            names_str = ", ".join(a.name for a in co_located)
            narrative = f"{names_str} are currently at the {location.name}, quietly busy with their schedules."

        # 4. Update SQLite
        for event in self.world.narrative_events:
            if event.get("id") == placeholder_id:
                event["narrative"] = narrative
                event["status"] = "completed"
                event["participants"] = [a.name for a in co_located]
                break

        # 5. Create new cognitive memories for all co-located agents
        for agent in co_located:
            await self.world.memory_engine.perceive_event(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                agent_occupation=agent.occupation,
                raw_event_description=narrative,
                location_name=location.name,
                timestamp=self.world.clock.current_time
            )

        # 6. Update Relationships (slightly increase trust of co-located agents due to shared time)
        for i, a1 in enumerate(co_located):
            for a2 in co_located[i+1:]:
                rel = a1.relationships.setdefault(
                    a2.agent_id, 
                    Relationship(trust=0.5, friendship=0.5, respect=0.5, fear=0.0, romantic=0.0, hidden_opinion="", shared_memory="")
                )
                rel.trust = min(1.0, rel.trust + 0.01)

        # 7. Generate new events
        self.world.event_bus.publish(
            Event(
                event_type=EventType.TICK,
                timestamp=self.world.clock.current_time,
                payload={"scene_narrative": narrative}
            )
        )

        # 8. Trigger Frontend Updates
        await ws_manager.broadcast({
            "type": "NARRATIVE_EVENT_COMPLETED",
            "payload": {
                "event_id": placeholder_id,
                "narrative": narrative,
                "status": "completed"
            }
        })

    async def generate_diary(self, agent_id: str) -> None:
        """Generate and record a diary entry for the agent based on today's thoughts.

        Args:
            agent_id: ID of the agent writing the diary.
        """
        agent = self.world.agent_manager.get(agent_id)
        if not agent:
            return

        memories = self.world.memory_manager.get_memories(agent_id)
        previous_diaries = [
            d["text"] for d in self.world.diaries.get(agent_id, [])
        ]

        # 1. Build token-minimized LLM Context
        ctx = ContextBuilder.build(
            reasoning_task="Diary Generation",
            current_agent=agent,
            relevant_memories=memories,
            player_influence={"previous_entries": previous_diaries}
        )

        # 2. Query LLM service
        res = await self.llm_service.reason("Diary Generation", ctx)

        # 3. Validate JSON payload
        diary_text = res.get("diary")
        if not diary_text or not isinstance(diary_text, str):
            logger.warning("BrainService: Invalid JSON response for Diary, using fallback.")
            diary_text = f"Another day passed. Spent it on my duties as {agent.occupation}."

        # 4. Update SQLite
        day, _ = self._get_time_info()
        entry = {
            "day": day,
            "label": f"Day {day} reflection",
            "text": diary_text,
        }
        self.world.diaries.setdefault(agent_id, []).append(entry)

        # 5. Create new cognitive memory of reflecting on their day
        await self.world.memory_engine.perceive_event(
            agent_id=agent_id,
            agent_name=agent.name,
            agent_occupation=agent.occupation,
            raw_event_description=f"Reflected on today in personal diary: '{diary_text}'",
            location_name=agent.location.name if agent.location else "Home",
            timestamp=self.world.clock.current_time,
            tags=["reflection", "diary"]
        )

        # 6. Generate new events
        self.world.event_bus.publish(
            Event(
                event_type=EventType.TICK,
                timestamp=self.world.clock.current_time,
                payload={"diary_written_by": agent.name}
            )
        )

        # 7. Trigger Frontend Updates
        await ws_manager.broadcast({
            "type": "DIARY_REFRESHED",
            "payload": {
                "agent_id": agent_id,
                "entry": entry
            }
        })

    async def generate_influence(self, agent_id: str, influence_type: str, details: str) -> None:
        """Generate a narrative describing the mental effects of a player nudge.

        Args:
            agent_id: ID of the agent receiving the nudge.
            influence_type: Nudge category (suggest/warn/comfort/encourage/etc).
            details: Context of the influence.
        """
        agent = self.world.agent_manager.get(agent_id)
        if not agent:
            return

        # 1. Build token-minimized LLM Context
        ctx = ContextBuilder.build(
            reasoning_task="Higher Self Reasoning",
            current_agent=agent,
            relationships=agent.relationships,
            current_scene=agent.location,
            player_influence={"type": influence_type, "details": details}
        )

        # 2. Query LLM service
        res = await self.llm_service.reason("Higher Self Reasoning", ctx)

        # 3. Validate JSON payload
        narrative = res.get("narrative")
        if not narrative or not isinstance(narrative, str):
            logger.warning("BrainService: Invalid JSON response for Player nudge, using fallback.")
            narrative = f"A subtle whisper shifts {agent.name}'s thoughts, nudging them toward: '{details}'."

        # 4. Update SQLite (Narrative events table)
        day, time_str = self._get_time_info()
        location_name = agent.location.name if agent.location else "Unknown"
        event_id = f"event_influence_{uuid.uuid4().hex[:8]}"
        event = {
            "id": event_id,
            "day": day,
            "time": time_str,
            "location": location_name,
            "type": "influence",
            "participants": [agent.name],
            "is_dialogue": False,
            "narrative": narrative,
        }
        self.world.narrative_events.append(event)

        # 5. Create new cognitive memory of the mental shift
        await self.world.memory_engine.perceive_event(
            agent_id=agent_id,
            agent_name=agent.name,
            agent_occupation=agent.occupation,
            raw_event_description=f"Felt a strange impulse: '{narrative}'",
            location_name=location_name,
            timestamp=self.world.clock.current_time,
            tags=["nudge", influence_type]
        )

        # 6. Update Relationships (if nudge is suggest/warn, slightly alter target trust)
        if influence_type.lower() == "warn":
            # Warn nudge makes agent more suspicious
            agent.suspicion = min(1.0, agent.suspicion + 0.15)
            # Find a target to decrease trust in
            for target_id in list(agent.relationships.keys())[:1]:
                rel = agent.relationships[target_id]
                rel.trust = max(0.0, rel.trust - 0.1)

        # 7. Generate new events
        self.world.event_bus.publish(
            Event(
                event_type=EventType.TICK,
                timestamp=self.world.clock.current_time,
                payload={"influence_applied": narrative}
            )
        )

        # 8. Trigger Frontend Updates
        await ws_manager.broadcast({
            "type": "INFLUENCE_APPLIED",
            "payload": {
                "event_id": event_id,
                "narrative": narrative,
                "agent_id": agent_id
            }
        })

    async def generate_question(self, agent_id: str, memories_summaries: list[str], question_text: str | None = None) -> str:
        """Asynchronously generate a dynamic dialogue response for agent interrogation.

        Args:
            agent_id: ID of the agent being questioned.
            memories_summaries: List of the summaries of memories the agent has.
            question_text: Optional custom question text.

        Returns:
            The generated dialogue string from the agent.
        """
        agent = self.world.agent_manager.get(agent_id)
        if not agent:
            return ""

        details_str = f"Interrogating about recollections: {memories_summaries}"
        if question_text:
            details_str = f"Interrogated with custom question: '{question_text}' | recollections context: {memories_summaries}"

        # 1. Build token-minimized LLM Context
        ctx = ContextBuilder.build(
            reasoning_task="Higher Self Reasoning",
            current_agent=agent,
            relationships=agent.relationships,
            current_scene=agent.location,
            player_influence={"type": "Interrogation", "details": details_str}
        )

        # 2. Query LLM service
        res = await self.llm_service.reason("Higher Self Reasoning", ctx)

        # 3. Validate JSON payload
        narrative = res.get("narrative")
        if not narrative or not isinstance(narrative, str):
            logger.warning("BrainService: Invalid JSON response for Interrogation, using fallback.")
            narrative = f"{agent.name} looks at you and says: 'I have shared all my recollections.'"

        # 4. Trigger Frontend Updates (Interrogation websocket message)
        await ws_manager.broadcast({
            "type": "INTERROGATION_COMPLETED",
            "payload": {
                "agent_id": agent_id,
                "response": narrative
            }
        })

        return narrative

    def _get_time_info(self) -> tuple[int, str]:
        """Helper to get current simulation day and formatted time string."""
        day = int(self.world.clock.current_time // 86400) + 1
        hours = int((self.world.clock.current_time % 86400) // 3600)
        minutes = int((self.world.clock.current_time % 3600) // 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        return day, time_str
