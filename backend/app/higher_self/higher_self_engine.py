"""HigherSelfEngine: translates player Influence into changes to the
city's cognitive state.

The Higher Self never changes the world directly. It only changes what
citizens know or believe. Everything else emerges from the existing
simulation.
"""

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
    "There's a thought I can't quite place.",
]

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
            id=f"mem_higher_self_{self._memory_manager.next_memory_id()}",            summary=summary,
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
        """Placeholder handler for REMEMBER. Not yet implemented."""
        return InfluenceResult(
            success=False,
            message="'remember' is not yet implemented.",
            affected_agents=[],
        )

    def _apply_warn(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for WARN. Not yet implemented."""
        return InfluenceResult(
            success=False,
            message="'warn' is not yet implemented.",
            affected_agents=[],
        )

    def _apply_comfort(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for COMFORT. Not yet implemented."""
        return InfluenceResult(
            success=False,
            message="'comfort' is not yet implemented.",
            affected_agents=[],
        )

    def _apply_encourage(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for ENCOURAGE. Not yet implemented."""
        return InfluenceResult(
            success=False,
            message="'encourage' is not yet implemented.",
            affected_agents=[],
        )

    def _apply_connect(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for CONNECT. Not yet implemented."""
        return InfluenceResult(
            success=False,
            message="'connect' is not yet implemented.",
            affected_agents=[],
        )

    def _apply_coincidence(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for COINCIDENCE. Not yet implemented."""
        return InfluenceResult(
            success=False,
            message="'coincidence' is not yet implemented.",
            affected_agents=[],
        )