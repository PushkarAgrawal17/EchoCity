"""LLMService: performs isolated AI reasoning tasks returning structured JSON."""

import json
import logging
from typing import Any
from app.llm.client import OllamaClient

logger = logging.getLogger(__name__)


class LLMService:
    """Isolated LLM reasoning service for EchoCity.

    Exposes a single public method `reason(task_type, context)` that queries
    the Ollama client using JSON mode and ensures strict structured outputs.
    """

    def __init__(self, ollama_client: OllamaClient) -> None:
        """Create an LLMService.

        Args:
            ollama_client: Client to interact with local Ollama model.
        """
        self.client = ollama_client

    async def reason(self, task_type: str, context: dict[str, Any]) -> dict[str, Any]:
        """Perform an isolated AI reasoning task.

        Args:
            task_type: The category of the task (e.g. 'Conversation', 'Planning').
            context: Context attributes used to build the prompts.

        Returns:
            A dictionary containing the parsed JSON keys.
        """
        task_type_lower = task_type.lower().replace(" ", "_")

        # Determine prompt builders and expected output keys
        if task_type_lower == "conversation":
            system, user = self._build_conversation_prompt(context)
            expected_keys = ["dialogue"]
        elif task_type_lower == "planning":
            system, user = self._build_planning_prompt(context)
            expected_keys = ["goal", "focus", "expected_mood"]
        elif task_type_lower == "crime_decision":
            system, user = self._build_crime_decision_prompt(context)
            expected_keys = ["commit_crime", "crime_type", "rationale", "method"]
        elif task_type_lower == "witness_reasoning":
            system, user = self._build_witness_reasoning_prompt(context)
            expected_keys = ["suspicion_increase", "will_report", "internal_explanation"]
"""LLMService: performs isolated AI reasoning tasks returning structured JSON."""

import json
import logging
from typing import Any
from app.llm.client import OllamaClient

logger = logging.getLogger(__name__)


class LLMService:
    """Isolated LLM reasoning service for EchoCity.

    Exposes a single public method `reason(task_type, context)` that queries
    the Ollama client using JSON mode and ensures strict structured outputs.
    """

    def __init__(self, ollama_client: OllamaClient) -> None:
        """Create an LLMService.

        Args:
            ollama_client: Client to interact with local Ollama model.
        """
        self.client = ollama_client

    async def reason(self, task_type: str, context: dict[str, Any]) -> dict[str, Any]:
        """Perform an isolated AI reasoning task.

        Args:
            task_type: The category of the task (e.g. 'Conversation', 'Planning').
            context: Context attributes used to build the prompts.

        Returns:
            A dictionary containing the parsed JSON keys.
        """
        task_type_lower = task_type.lower().replace(" ", "_")

        # Determine prompt builders and expected output keys
        if task_type_lower == "conversation":
            system, user = self._build_conversation_prompt(context)
            expected_keys = ["dialogue"]
        elif task_type_lower == "planning":
            system, user = self._build_planning_prompt(context)
            expected_keys = ["goal", "focus", "expected_mood"]
        elif task_type_lower == "crime_decision":
            system, user = self._build_crime_decision_prompt(context)
            expected_keys = ["commit_crime", "crime_type", "rationale", "method"]
        elif task_type_lower == "witness_reasoning":
            system, user = self._build_witness_reasoning_prompt(context)
            expected_keys = ["suspicion_increase", "will_report", "internal_explanation"]
        elif task_type_lower == "diary_generation":
            system, user = self._build_diary_prompt(context)
            expected_keys = ["diary"]
        elif task_type_lower == "memory_compression":
            system, user = self._build_memory_compression_prompt(context)
            expected_keys = ["summarized_belief", "key_evidence", "suspect_ratings"]
        elif task_type_lower == "investigation_report":
            system, user = self._build_investigation_report_prompt(context)
            expected_keys = ["summary_of_charges", "prosecution_strength", "court_recommendation"]
        elif task_type_lower == "higher_self_reasoning":
            system, user = self._build_higher_self_prompt(context)
            expected_keys = ["narrative"]
        elif task_type_lower == "event_compression":
            system, user = self._build_event_compression_prompt(context)
            expected_keys = ["summary", "emotion", "importance", "tags"]
        else:
            raise ValueError(f"Unsupported task_type: {task_type}")

        # Send structured request to local Qwen instance
        try:
            raw_response = await self.client.generate(user, system_prompt=system, format_type="json")
            data = json.loads(raw_response)

            # Ensure all expected keys exist in the returned dictionary
            for key in expected_keys:
                if key not in data:
                    data[key] = self._get_fallback_value(key)
            return data

        except Exception as e:
            logger.error("LLMService reasoning failed for task: %s, using fallback. Error: %s", task_type, e)
            # Return full fallback schema
            return {key: self._get_fallback_value(key, context) for key in expected_keys}

    def _get_fallback_value(self, key: str, context: dict | None = None) -> Any:
        """Provide safe fallback values matching the expected key data types."""
        if key == "commit_crime":
            return False
        if key == "will_report":
            return False
        if key == "suspicion_increase":
            return 0.0
        if key == "key_evidence":
            return []
        if key == "suspect_ratings":
            return {}
        if key == "dialogue":
            return "..."
        if key == "diary":
            return "Another quiet day."
        if key == "goal":
            return "Going about scheduled duties."
        if key == "focus":
            return "Normal routine."
        if key == "expected_mood":
            return "calm"
        if key == "rationale" or key == "method":
            return "N/A"
        if key == "crime_type":
            return "none"
        if key == "summarized_belief":
            return "Nothing out of the ordinary."
        if key == "summary_of_charges":
            return "No charges filed."
        if key == "prosecution_strength":
            return "weak"
        if key == "court_recommendation":
            return "dismissal"
        if key == "narrative":
            return "A passing thought shifts their focus."
        if key == "importance":
            return 0.5
        if key == "tags":
            return []
        if key == "emotion":
            return "neutral"
        if key == "summary":
            return "Event observed."
        return ""

    # --- Prompt Builders ---

    def _build_conversation_prompt(self, ctx: dict) -> tuple[str, str]:
        system = "JSON only: {'dialogue': 'short character conversation'}"
        user = (
            f"Speaker: {ctx.get('speaker')} ({ctx.get('speaker_occupation')})\n"
            f"Listener: {ctx.get('listener')} ({ctx.get('listener_occupation')})\n"
            f"Location: {ctx.get('location')}\n"
            f"Topic: {ctx.get('memory')}\n"
            f"Generate 2-4 lines of natural dialogue."
        )
        return system, user

    def _build_planning_prompt(self, ctx: dict) -> tuple[str, str]:
        system = "JSON only: {'goal': 'str', 'focus': 'str', 'expected_mood': 'str'}"
        user = (
            f"Agent: {ctx.get('agent_name')} ({ctx.get('occupation')})\n"
            f"Traits: {ctx.get('traits')}\n"
            f"Needs: {ctx.get('needs')}\n"
            f"Time: {ctx.get('time')}\n"
            f"Activity: {ctx.get('schedule_activity')}\n"
            f"Plan focus, goal, and mood."
        )
        return system, user

    def _build_crime_decision_prompt(self, ctx: dict) -> tuple[str, str]:
        system = "JSON only: {'commit_crime': bool, 'crime_type': 'str', 'rationale': 'str', 'method': 'str'}"
        user = (
            f"Agent: {ctx.get('agent_name')}\n"
            f"Opportunity: {ctx.get('opportunity')}\n"
            f"State: {ctx.get('stress')}, {ctx.get('suspicion')}\n"
            f"Traits: {ctx.get('personality')}\n"
            f"Secrets: {ctx.get('secrets')}\n"
            f"Determine if they commit a crime."
        )
        return system, user

    def _build_witness_reasoning_prompt(self, ctx: dict) -> tuple[str, str]:
        system = "JSON only: {'suspicion_increase': float, 'will_report': bool, 'internal_explanation': 'str'}"
        user = (
            f"Agent: {ctx.get('agent_name')}\n"
            f"Witnessed: '{ctx.get('witnessed_event')}'\n"
            f"Trust: {ctx.get('trust_in_culprit')} | Fear: {ctx.get('fear_of_culprit')}\n"
            f"Determine suspicion change and if they report."
        )
        return system, user

    def _build_diary_prompt(self, ctx: dict) -> tuple[str, str]:
        system = "JSON only: {'diary': 'first-person diary entry text'}"
        user = (
            f"Agent: {ctx.get('agent_name')} ({ctx.get('occupation')})\n"
            f"Traits: {ctx.get('personality')}\n"
            f"Memories:\n{ctx.get('recent_memories')}\n"
            f"Context:\n{ctx.get('previous_entries')}\n"
            f"Write a brief reflective diary entry."
        )
        return system, user

    def _build_memory_compression_prompt(self, ctx: dict) -> tuple[str, str]:
        system = "JSON only: {'summarized_belief': 'str', 'key_evidence': ['str'], 'suspect_ratings': {'name': float}}"
        user = (
            f"Agent: {ctx.get('agent_name')}\n"
            f"Memories:\n{ctx.get('memories')}\n"
            f"Consolidate beliefs and suspect levels."
        )
        return system, user

    def _build_investigation_report_prompt(self, ctx: dict) -> tuple[str, str]:
        system = "JSON only: {'summary_of_charges': 'str', 'prosecution_strength': 'str', 'court_recommendation': 'str'}"
        user = (
            f"Detective: {ctx.get('detective_name')}\n"
            f"Accused: {ctx.get('accused_name')}\n"
            f"Evidence:\n{ctx.get('evidence_summaries')}\n"
            f"Generate investigation report summary."
        )
        return system, user

    def _build_higher_self_prompt(self, ctx: dict) -> tuple[str, str]:
        system = "JSON only: {'narrative': 'short narrative text'}"
        user = (
            f"Context: {ctx.get('details')}\n"
            f"Agent: {ctx.get('agent_name')}\n"
            f"Nudge: {ctx.get('influence_type')}\n"
            f"State: {ctx.get('current_state')}\n"
            f"Describe psychological impact/scene description."
        )
        return system, user

    def _build_event_compression_prompt(self, ctx: dict) -> tuple[str, str]:
        system = "JSON only: {'summary': 'short compressed description', 'emotion': 'str', 'importance': float, 'tags': ['str']}"
        user = (
            f"Agent: {ctx.get('agent_name')} ({ctx.get('occupation')})\n"
            f"Event details: {ctx.get('raw_event')}\n"
            f"Compress this event into a memory for the agent."
        )
        return system, user
