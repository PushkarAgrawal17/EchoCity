"""MemoryEngine: processes raw simulation events into compressed cognitive memories."""

import logging
import re
from typing import Any, List
from app.llm.llm_service import LLMService
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType

logger = logging.getLogger(__name__)


class MemoryEngine:
    """Cognitive memory engine for EchoCity.

    Receives raw events, executes LLM-based event compression on interactive
    scenes or dialogues, and generates structured Memory objects for storage.
    Uses rule-based fallbacks for routine events to minimize CPU latency.
    """

    def __init__(self, llm_service: LLMService, memory_manager: MemoryManager) -> None:
        """Create a MemoryEngine.

        Args:
            llm_service: Service to make LLM calls.
            memory_manager: Storage manager for memories.
        """
        self.llm_service = llm_service
        self.memory_manager = memory_manager

    @staticmethod
    def extract_participants(text: str) -> List[str]:
        """Statically extract agent names present in the event text to save tokens."""
        names_map = {
            "marcus": "Marcus Hale",
            "ethan": "Ethan Cross",
            "ava": "Ava Morgan",
            "noah": "Noah Reed",
            "emma": "Emma Brooks",
            "liam": "Liam Carter",
            "sophia": "Sophia Bennett",
            "victor": "Victor Kane",
            "alice": "Alice",
            "bob": "Bob",
            "carol": "Carol",
            "dave": "Dave",
            "frank": "Frank",
            "grace": "Grace",
            "henry": "Henry"
        }
        found = set()
        text_lower = text.lower()
        for first_name, full_name in names_map.items():
            # Match boundary to prevent partial matches like "carol" in "caroline"
            if re.search(rf"\b{first_name}\b", text_lower):
                found.add(full_name)
        return list(found)

    @staticmethod
    def is_complex_event(text: str) -> bool:
        """Determine if an event is interactive/complex enough to warrant LLM compression."""
        keywords = [
            "argued", "stole", "theft", "court", "witnessed", "whispers", 
            "says", "said", "clue", "guilty", "convicted", "acquitted", 
            "secret", "evidence", "suspicious", "accident", "investigation",
            "dialogue", "@", ":"
        ]
        text_lower = text.lower()
        return any(k in text_lower for k in keywords)

    async def perceive_event(
        self,
        agent_id: str,
        agent_name: str,
        agent_occupation: str,
        raw_event_description: str,
        location_name: str,
        timestamp: float,
        source: str = "self",
        memory_type: MemoryType = MemoryType.PERSONAL,
        subject_id: str | None = None
    ) -> Memory:
        """Perceive a raw simulation event and store it as a compressed Memory.

        Args:
            agent_id: ID of the agent perceiving the event.
            agent_name: Name of the perceiving agent.
            agent_occupation: Occupation of the perceiving agent.
            raw_event_description: Detailed text description of the event.
            location_name: Location where the event occurred.
            timestamp: Simulation time.
            source: Source of the event (e.g. "self" or another agent's ID).
            memory_type: Classification of the memory.
            subject_id: Optional ID of another agent of interest.

        Returns:
            The structured and stored Memory object.
        """
        participants = self.extract_participants(raw_event_description)
        if agent_name not in participants:
            participants.append(agent_name)

        # 1. Determine if we can bypass LLM to minimize latency
        if not self.is_complex_event(raw_event_description):
            # Fast-path: Rule-based compression for routine activities
            summary = raw_event_description.strip()
            emotion = "neutral"
            importance = 0.1
            tags = ["routine"]
        else:
            # Slow-path: Query LLM to compress dialogue/incident/crime/social interactions
            ctx = {
                "agent_name": agent_name,
                "occupation": agent_occupation,
                "raw_event": raw_event_description
            }
            try:
                res = await self.llm_service.reason("event_compression", ctx)
                summary = res.get("summary", raw_event_description)
                emotion = res.get("emotion", "neutral")
                importance = float(res.get("importance", 0.5))
                tags = res.get("tags", ["general"])
            except Exception as e:
                logger.error("Failed to compress memory for %s: %s", agent_name, e)
                summary = raw_event_description
                emotion = "neutral"
                importance = 0.3
                tags = ["general"]

        # 2. Construct Memory object
        memory_id = self.memory_manager.next_memory_id()
        memory_obj = Memory(
            id=memory_id,
            summary=summary,
            type=memory_type,
            source=source,
            timestamp=timestamp,
            confidence=1.0,
            shared=False,
            subject_id=subject_id,
            emotion=emotion,
            importance=importance,
            participants=participants,
            location=location_name,
            tags=tags
        )

        # 3. Save to storage
        self.memory_manager.add_memory(agent_id, memory_obj)
        return memory_obj
