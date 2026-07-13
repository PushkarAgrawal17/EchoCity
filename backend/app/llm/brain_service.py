"""BrainService: orchestrates local AI prompt construction, inference, and world updates."""

import logging
import uuid
from typing import Any
from app.conversation.conversation import Conversation
from app.llm.client import OllamaClient
from app.llm.llm_service import LLMService
from app.simulation.world import World

logger = logging.getLogger(__name__)


class BrainService:
    """Orchestrates local AI generation of gossip, scene narratives, diaries, and influences.

    Delegates all model execution to LLMService.reason() to return validated
    JSON structures, then updates the active simulation World.
    """

    def __init__(self, world: World, ollama_client: OllamaClient) -> None:
        """Create a BrainService.

        Args:
            world: The simulation World instance to update.
            ollama_client: Client for Ollama inference.
        """
        self.world = world
        self.client = ollama_client
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
        memory_summary = memory.summary if memory else "something interesting"
        location_name = speaker.location.name if speaker.location else "Cafe"

        # Build LLM Context
        ctx = {
            "speaker": speaker.name,
            "speaker_occupation": speaker.occupation,
            "speaker_speech": speaker.speech_style,
            "listener": listener.name,
            "listener_occupation": listener.occupation,
            "listener_speech": listener.speech_style,
            "location": location_name,
            "memory": memory_summary,
        }

        # Query isolated LLM service
        res = await self.llm_service.reason("Conversation", ctx)
        dialogue = res.get("dialogue", f"{speaker.name} whispers to {listener.name}: '{memory_summary}'.")

        # Find and update the placeholder event in-place
        for event in self.world.narrative_events:
            if event.get("id") == placeholder_id:
                event["narrative"] = dialogue
                event["status"] = "completed"
                break

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

        agents_info = [
            {
                "name": a.name,
                "occupation": a.occupation,
                "goal": a.goal or "Going about their day",
                "emotion": a.emotion,
                "stress": a.stress,
                "suspicion": a.suspicion,
                "secrets": a.secrets,
            }
            for a in co_located
        ]

        # Build LLM Context
        ctx = {
            "details": f"Narrating physical location scene for agents co-located at the {location.name}.",
            "agent_name": ", ".join(a.name for a in co_located),
            "influence_type": "Observation",
            "current_state": {"agents": agents_info},
        }

        # Query isolated LLM service
        res = await self.llm_service.reason("Higher Self Reasoning", ctx)
        narrative = res.get("narrative")
        if not narrative:
            names_str = ", ".join(a.name for a in co_located)
            narrative = f"{names_str} are currently at the {location.name}, quietly busy with their schedules."

        # Find and update the placeholder event in-place
        for event in self.world.narrative_events:
            if event.get("id") == placeholder_id:
                event["narrative"] = narrative
                event["status"] = "completed"
                event["participants"] = [a.name for a in co_located]
                break

    async def generate_diary(self, agent_id: str) -> None:
        """Generate and record a diary entry for the agent based on today's thoughts.

        Args:
            agent_id: ID of the agent writing the diary.
        """
        agent = self.world.agent_manager.get(agent_id)
        if not agent:
            return

        memories = self.world.memory_manager.get_memories(agent_id)
        recent_summaries = [m.summary for m in memories]
        if not recent_summaries:
            recent_summaries = ["Spent the day going about my schedule quietly."]

        previous_diaries = [
            d["text"] for d in self.world.diaries.get(agent_id, [])
        ]

        # Build LLM Context
        ctx = {
            "agent_name": agent.name,
            "occupation": agent.occupation,
            "personality": agent.personality,
            "recent_memories": recent_summaries,
            "previous_entries": previous_diaries,
        }

        # Query isolated LLM service
        res = await self.llm_service.reason("Diary Generation", ctx)
        diary_text = res.get("diary", f"Another day passed. Spent it on my duties as {agent.occupation}.")

        day, _ = self._get_time_info()
        entry = {
            "day": day,
            "label": f"Day {day} reflection",
            "text": diary_text,
        }
        self.world.diaries.setdefault(agent_id, []).append(entry)

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

        current_state = {
            "goal": agent.goal,
            "emotion": agent.emotion,
            "stress": agent.stress,
            "suspicion": agent.suspicion,
        }

        # Build LLM Context
        ctx = {
            "details": details,
            "agent_name": agent.name,
            "influence_type": influence_type,
            "current_state": current_state,
        }

        # Query isolated LLM service
        res = await self.llm_service.reason("Higher Self Reasoning", ctx)
        narrative = res.get("narrative", f"A subtle whisper shifts {agent.name}'s thoughts, nudging them toward: '{details}'.")

        day, time_str = self._get_time_info()
        location_name = agent.location.name if agent.location else "Unknown"
        event = {
            "id": f"event_influence_{uuid.uuid4().hex[:8]}",
            "day": day,
            "time": time_str,
            "location": location_name,
            "type": "influence",
            "participants": [agent.name],
            "is_dialogue": False,
            "narrative": narrative,
        }
        self.world.narrative_events.append(event)

    async def generate_question(self, agent_id: str, memories_summaries: list[str]) -> str:
        """Asynchronously generate a dynamic dialogue response for agent interrogation.

        Args:
            agent_id: ID of the agent being questioned.
            memories_summaries: List of the summaries of memories the agent has.

        Returns:
            The generated dialogue string from the agent.
        """
        agent = self.world.agent_manager.get(agent_id)
        if not agent:
            return ""

        # Build LLM Context
        ctx = {
            "details": f"Interrogating about recollections: {memories_summaries}",
            "agent_name": agent.name,
            "influence_type": "Interrogation",
            "current_state": {"traits": agent.personality, "secrets": agent.secrets},
        }

        # Query isolated LLM service (using Higher Self Reasoning schema)
        res = await self.llm_service.reason("Higher Self Reasoning", ctx)
        return res.get("narrative", f"{agent.name} looks at you and says: 'I have shared all my recollections.'")

    def _get_time_info(self) -> tuple[int, str]:
        """Helper to get current simulation day and formatted time string."""
        day = int(self.world.clock.current_time // 86400) + 1
        hours = int((self.world.clock.current_time % 86400) // 3600)
        minutes = int((self.world.clock.current_time % 3600) // 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        return day, time_str
