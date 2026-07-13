"""BrainService: orchestrates local AI prompt construction, inference, and world updates."""

import json
import logging
import uuid
from typing import Any
from app.conversation.conversation import Conversation
from app.llm.client import OllamaClient
from app.llm.prompt_builder import PromptBuilder
from app.simulation.world import World

logger = logging.getLogger(__name__)


class BrainService:
    """Orchestrates local AI generation of gossip, scene narratives, diaries, and influences.

    Communicates with OllamaClient, runs prompts through PromptBuilder, validates
    JSON outputs, and applies the narrative/state updates back to the World.
    """

    def __init__(self, world: World, ollama_client: OllamaClient) -> None:
        """Create a BrainService.

        Args:
            world: The simulation World instance to update.
            ollama_client: Client for Ollama inference.
        """
        self.world = world
        self.client = ollama_client
        self.prompt_builder = PromptBuilder()

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

        system, prompt = self.prompt_builder.build_gossip_prompt(
            speaker_name=speaker.name,
            speaker_occupation=speaker.occupation,
            speaker_speech=speaker.speech_style,
            listener_name=listener.name,
            listener_occupation=listener.occupation,
            listener_speech=listener.speech_style,
            location_name=location_name,
            memory_summary=memory_summary,
        )

        try:
            raw_response = await self.client.generate(prompt, system_prompt=system, format_type="json")
            data = json.loads(raw_response)
            dialogue = data.get("dialogue", "")
        except Exception as e:
            logger.error("BrainService gossip generation failed, using fallback: %s", e)
            dialogue = f"{speaker.name} whispers to {listener.name}: '{memory_summary}'."

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

        recent_narratives = [
            e["narrative"] for e in self.world.narrative_events[-5:]
            if e.get("narrative") and e.get("id") != placeholder_id
        ]

        system, prompt = self.prompt_builder.build_scene_prompt(
            location_name=location.name,
            agents_info=agents_info,
            recent_events=recent_narratives,
        )

        try:
            raw_response = await self.client.generate(prompt, system_prompt=system, format_type="json")
            data = json.loads(raw_response)
            narrative = data.get("narrative", "")
        except Exception as e:
            logger.error("BrainService scene generation failed, using fallback: %s", e)
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

        system, prompt = self.prompt_builder.build_diary_prompt(
            agent_name=agent.name,
            occupation=agent.occupation,
            personality=agent.personality,
            recent_memories=recent_summaries,
            previous_entries=previous_diaries,
        )

        try:
            raw_response = await self.client.generate(prompt, system_prompt=system, format_type="json")
            data = json.loads(raw_response)
            diary_text = data.get("diary", "")
        except Exception as e:
            logger.error("BrainService diary generation failed, using fallback: %s", e)
            diary_text = f"Another day passed. Spent it on my duties as {agent.occupation}."

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

        system, prompt = self.prompt_builder.build_influence_prompt(
            agent_name=agent.name,
            influence_type=influence_type,
            details=details,
            current_state=current_state,
        )

        try:
            raw_response = await self.client.generate(prompt, system_prompt=system, format_type="json")
            data = json.loads(raw_response)
            narrative = data.get("narrative", "")
        except Exception as e:
            logger.error("BrainService influence narrative generation failed: %s", e)
            narrative = f"A subtle whisper shifts {agent.name}'s thoughts, nudging them toward: '{details}'."

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

    def _get_time_info(self) -> tuple[int, str]:
        """Helper to get current simulation day and formatted time string."""
        day = int(self.world.clock.current_time // 86400) + 1
        hours = int((self.world.clock.current_time % 86400) // 3600)
        minutes = int((self.world.clock.current_time % 3600) // 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        return day, time_str

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

        system, prompt = self.prompt_builder.build_question_prompt(
            agent_name=agent.name,
            occupation=agent.occupation,
            traits=agent.personality,
            secrets=agent.secrets,
            memories_summaries=memories_summaries,
        )

        try:
            raw_response = await self.client.generate(prompt, system_prompt=system, format_type="json")
            data = json.loads(raw_response)
            return str(data.get("dialogue", ""))
        except Exception as e:
            logger.error("BrainService generate_question failed, using fallback: %s", e)
            return f"{agent.name} looks at you and says: 'I have shared all my recollections. What else is there to tell?'"
