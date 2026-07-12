"""HigherSelfEngine: translates player Influence into changes to the
city's cognitive state.

The Higher Self never changes the world directly. It only changes what
citizens know or believe. Everything else emerges from the existing
simulation.
"""

from collections.abc import Callable

from app.agents.agent_manager import AgentManager
from app.higher_self.influence import Influence
from app.higher_self.influence_result import InfluenceResult
from app.higher_self.influence_type import InfluenceType
from app.memory.memory_manager import MemoryManager


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
        self._handlers: dict[InfluenceType, Callable[[Influence], InfluenceResult]] = {
            InfluenceType.SUGGEST: self._apply_suggest,
            InfluenceType.REMEMBER: self._apply_remember,
            InfluenceType.WARN: self._apply_warn,
            InfluenceType.COMFORT: self._apply_comfort,
            InfluenceType.ENCOURAGE: self._apply_encourage,
            InfluenceType.CONNECT: self._apply_connect,
            InfluenceType.COINCIDENCE: self._apply_coincidence,
        }

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

        handler = self._handlers[influence.type]
        return handler(influence)

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
        """Placeholder handler for SUGGEST. Not yet implemented."""
        return self._not_implemented(influence)

    def _apply_remember(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for REMEMBER. Not yet implemented."""
        return self._not_implemented(influence)

    def _apply_warn(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for WARN. Not yet implemented."""
        return self._not_implemented(influence)

    def _apply_comfort(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for COMFORT. Not yet implemented."""
        return self._not_implemented(influence)

    def _apply_encourage(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for ENCOURAGE. Not yet implemented."""
        return self._not_implemented(influence)

    def _apply_connect(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for CONNECT. Not yet implemented."""
        return self._not_implemented(influence)

    def _apply_coincidence(self, influence: Influence) -> InfluenceResult:
        """Placeholder handler for COINCIDENCE. Not yet implemented."""
        return self._not_implemented(influence)

    def _not_implemented(self, influence: Influence) -> InfluenceResult:
        """Return a placeholder result for an influence type not yet built.

        Args:
            influence: The influence that was dispatched.

        Returns:
            A failed InfluenceResult noting the type is unimplemented.
        """
        return InfluenceResult(
            success=False,
            message=f"'{influence.type.value}' is not yet implemented.",
            affected_agents=[],
        )