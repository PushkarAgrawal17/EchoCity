"""HigherSelfEngine: translates player Influence into changes to the
city's cognitive state.

The Higher Self never changes the world directly. It only changes what
citizens know or believe. Everything else emerges from the existing
simulation.
"""

from collections.abc import Sequence
from dataclasses import replace

from app.agents.agent_manager import AgentManager
from app.higher_self.influence import Influence
from app.higher_self.influence_result import InfluenceResult
from app.higher_self.influence_type import InfluenceType
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType

_SUGGEST_TEMPLATES = [
    "I have a feeling something isn't right.",
    "Something about today feels off.",
    "I can't shake this feeling of unease.",
]

_WARN_TEMPLATES = [
    "Something feels dangerous about this place.",
    "I should be careful about who I trust.",
    "I have a bad feeling about what's coming.",
]

_COMFORT_TEMPLATES = [
    "It's going to be alright.",
    "I don't need to worry so much.",
    "Things will work out in the end.",
]

_ENCOURAGE_TEMPLATES = [
    "I can handle whatever happens next.",
    "I should trust my own judgment more.",
    "I'm capable of figuring this out.",
]

_COINCIDENCE_CONFIDENCE_BOOST = 0.2


class HigherSelfEngine:
    """Applies player Influences to the city's cognitive state.

    HigherSelfEngine is the sole entry point for player influence over
    NPC cognition. It depends only on MemoryManager and AgentManager,
    and never mutates Agent state, Crime state, or triggers Gossip or
    Conversation directly.
    """

    def __init__(self, memory_manager: MemoryManager, agent_manager: AgentManager) -> None:
        """Create a HigherSelfEngine.

        Args:
            memory_manager: Owns the city's memories.
            agent_manager: Read-only source for validating agent targets.
        """
        self._memory_manager = memory_manager
        self._agent_manager = agent_manager

    def apply(self, influence: Influence) -> InfluenceResult:
        """Apply an Influence to the city's cognitive state.

        Args:
            influence: The player's expressed intent.

        Returns:
            An InfluenceResult describing the outcome.
        """
        validation_error = self._validate_targets(influence)
        if validation_error is not None:
            return validation_error

        match influence.type:
            case InfluenceType.SUGGEST:
                return self._apply_suggest(influence)
            case InfluenceType.REMEMBER:
                return self._apply_remember(influence)
            case InfluenceType.WARN:
                return self._apply_warn(influence)
            case InfluenceType.COMFORT:
                return self._apply_comfort(influence)
            case InfluenceType.ENCOURAGE:
                return self._apply_encourage(influence)
            case InfluenceType.CONNECT:
                return self._apply_connect(influence)
            case InfluenceType.COINCIDENCE:
                return self._apply_coincidence(influence)
            case _:
                raise AssertionError(f"Unhandled InfluenceType: {influence.type}")

    def _validate_targets(self, influence: Influence) -> InfluenceResult | None:
        """Validate that the agent(s) targeted by an Influence exist.

        Args:
            influence: The influence whose targets should be checked.

        Returns:
            An InfluenceResult describing failure if a target is
            missing, or None if validation passed.
        """
        if self._agent_manager.get(influence.primary_target) is None:
            return InfluenceResult(
                success=False,
                message=f"Unknown agent '{influence.primary_target}'.",
                affected_agents=[],
            )

        if (
            influence.secondary_target is not None
            and self._agent_manager.get(influence.secondary_target) is None
        ):
            return InfluenceResult(
                success=False,
                message=f"Unknown agent '{influence.secondary_target}'.",
                affected_agents=[],
            )

        return None

    def _apply_suggest(self, influence: Influence) -> InfluenceResult:
        """Plant a vague suspicion in the target's mind.

        Creates a low-confidence PERSONAL memory with no subject_id,
        so it can never be mistaken for evidence pointing at anyone.
        """
        memory_count = len(self._memory_manager.get_memories(influence.primary_target))
        summary = _SUGGEST_TEMPLATES[memory_count % len(_SUGGEST_TEMPLATES)]

        memory = Memory(
            id=f"mem_higher_self_{self._memory_manager.next_memory_id()}",
            summary=summary,
            type=MemoryType.PERSONAL,
            source="self",
            timestamp=0.0,
            confidence=0.3,
        )
        self._memory_manager.add_memory(influence.primary_target, memory)

        return InfluenceResult(
            success=True,
            message="A subtle influence has taken hold.",
            affected_agents=[influence.primary_target],
        )

    def _apply_remember(self, influence: Influence) -> InfluenceResult:
        """Resurface a memory the target already holds.

        Duplicates an existing memory under a fresh id. Never invents
        new knowledge — fails if the referenced memory doesn't exist.
        """
        if influence.reference is None:
            return InfluenceResult(
                success=False,
                message="No memory reference was provided.",
                affected_agents=[],
            )

        original = self._memory_manager.get_memory(influence.primary_target, influence.reference)
        if original is None:
            return InfluenceResult(
                success=False,
                message=f"No such memory '{influence.reference}' to remember.",
                affected_agents=[],
            )

        resurfaced = replace(
            original,
            id=f"mem_higher_self_{self._memory_manager.next_memory_id()}",
            timestamp=0.0,
        )
        self._memory_manager.add_memory(influence.primary_target, resurfaced)

        return InfluenceResult(
            success=True,
            message="A memory has resurfaced.",
            affected_agents=[influence.primary_target],
        )

    def _apply_warn(self, influence: Influence) -> InfluenceResult:
        """Instill a vague sense of danger or caution."""
        return self._apply_template_influence(
            influence, _WARN_TEMPLATES, "A sense of caution has taken hold."
        )

    def _apply_comfort(self, influence: Influence) -> InfluenceResult:
        """Instill vague reassurance."""
        return self._apply_template_influence(
            influence, _COMFORT_TEMPLATES, "A sense of comfort has taken hold."
        )

    def _apply_encourage(self, influence: Influence) -> InfluenceResult:
        """Instill a vague positive expectation."""
        return self._apply_template_influence(
            influence, _ENCOURAGE_TEMPLATES, "A sense of encouragement has taken hold."
        )

    def _apply_connect(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for CONNECT. Not yet implemented."""
        return InfluenceResult(
            success=False,
            message="'connect' is not yet implemented.",
            affected_agents=[],
        )

    def _apply_coincidence(self, influence: Influence) -> InfluenceResult:
        """Resurface a memory the target already holds, as a spontaneous
        realization.

        Mechanically identical to REMEMBER's resurfacing — the distinct
        gameplay effect comes from GossipEngine's per-speaker rotation,
        which now makes an appended memory eligible for a future
        conversation rather than being permanently unreachable.
        """
        if influence.reference is None:
            return InfluenceResult(
                success=False,
                message="No memory reference was provided.",
                affected_agents=[],
            )

        original = self._memory_manager.get_memory(influence.primary_target, influence.reference)
        if original is None:
            return InfluenceResult(
                success=False,
                message=f"No such memory '{influence.reference}' for coincidence.",
                affected_agents=[],
            )

        resurfaced = replace(
            original,
            id=f"mem_higher_self_{self._memory_manager.next_memory_id()}",
            timestamp=0.0,
        )
        self._memory_manager.add_memory(influence.primary_target, resurfaced)

        return InfluenceResult(
            success=True,
            message="A coincidence has drawn new attention to something already known.",
            affected_agents=[influence.primary_target],
        )

    def _apply_template_influence(
        self, influence: Influence, templates: Sequence[str], success_message: str
    ) -> InfluenceResult:
        """Shared mechanic for template-based, fact-free influences."""
        memory_count = len(self._memory_manager.get_memories(influence.primary_target))
        summary = templates[memory_count % len(templates)]

        memory = Memory(
            id=f"mem_higher_self_{self._memory_manager.next_memory_id()}",
            summary=summary,
            type=MemoryType.PERSONAL,
            source="self",
            timestamp=0.0,
            confidence=0.3,
        )
        self._memory_manager.add_memory(influence.primary_target, memory)

        return InfluenceResult(
            success=True,
            message=success_message,
            affected_agents=[influence.primary_target],
        )
