"""HigherSelfEngine: translates player Influence into changes to the
city's cognitive state.

The Higher Self never changes the world directly. It only changes what
citizens know or believe. Everything else emerges from the existing
simulation.
"""

from collections.abc import Callable

from app.agents.agent import Agent
from app.agents.agent_manager import AgentManager
from app.higher_self.higher_self_engine import HigherSelfEngine
from app.higher_self.influence import Influence
from app.higher_self.influence_result import InfluenceResult
from app.higher_self.influence_type import InfluenceType
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType


def _make_memory_manager_with_memory(agent_id: str, memory_id: str) -> MemoryManager:
    """Create a MemoryManager seeded with one memory."""
    manager = MemoryManager()
    manager.add_memory(
        agent_id,
        Memory(
            id=memory_id,
            summary="Saw Emma leave the Cafe.",
            type=MemoryType.WITNESS,
            source="self",
            timestamp=5.0,
            confidence=0.9,
            subject_id="agent_2",
        ),
    )
    return manager


def _make_engine_with_agent(
    agent_id: str = "agent_1",
) -> tuple[HigherSelfEngine, MemoryManager]:
    """Create a HigherSelfEngine with one registered agent."""
    memory_manager = MemoryManager()
    agent_manager = AgentManager()
    agent_manager.register(Agent(agent_id=agent_id, name="Agent One"))
    engine = HigherSelfEngine(memory_manager, agent_manager)
    return engine, memory_manager


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

    def test_suggest_adds_one_memory() -> None:
        """SUGGEST should add exactly one memory to the target agent."""
        memory_manager = MemoryManager()
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        result = engine.apply(Influence(type=InfluenceType.SUGGEST, primary_target="agent_1"))

        assert result.success is True
        assert result.affected_agents == ["agent_1"]
        assert len(memory_manager.get_memories("agent_1")) == 1

    def test_suggest_memory_has_no_subject_id() -> None:
        """SUGGEST must never point at a specific agent as subject."""
        memory_manager = MemoryManager()
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        engine.apply(Influence(type=InfluenceType.SUGGEST, primary_target="agent_1"))

        memory = memory_manager.get_memories("agent_1")[0]
        assert memory.subject_id is None

    def test_remember_duplicates_existing_memory() -> None:
        """A successful REMEMBER should add a copy of the referenced memory."""
        memory_manager = _make_memory_manager_with_memory("agent_1", "mem_a")
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        result = engine.apply(
            Influence(type=InfluenceType.REMEMBER, primary_target="agent_1", reference="mem_a")
        )

        assert result.success is True
        assert len(memory_manager.get_memories("agent_1")) == 2

    def test_remember_new_copy_has_different_id() -> None:
        """The resurfaced memory must have a fresh id, not the original's."""
        memory_manager = _make_memory_manager_with_memory("agent_1", "mem_a")
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        engine.apply(
            Influence(type=InfluenceType.REMEMBER, primary_target="agent_1", reference="mem_a")
        )

        ids = [m.id for m in memory_manager.get_memories("agent_1")]
        assert len(set(ids)) == 2

    def test_remember_does_not_mutate_original() -> None:
        """The original memory must remain untouched after REMEMBER."""
        memory_manager = _make_memory_manager_with_memory("agent_1", "mem_a")
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        engine.apply(
            Influence(type=InfluenceType.REMEMBER, primary_target="agent_1", reference="mem_a")
        )

        original = memory_manager.get_memory("agent_1", "mem_a")
        assert original is not None
        assert original.summary == "Saw Emma leave the Cafe."
        assert original.confidence == 0.9

    def test_remember_missing_reference_fails() -> None:
        """REMEMBER with no reference should fail without creating a memory."""
        engine, memory_manager = _make_engine_with_agent()

        result = engine.apply(Influence(type=InfluenceType.REMEMBER, primary_target="agent_1"))

        assert result.success is False
        assert memory_manager.get_memories("agent_1") == []

    def test_remember_unknown_memory_fails() -> None:
        """REMEMBER pointing at a nonexistent memory should fail cleanly."""
        engine, memory_manager = _make_engine_with_agent()

        result = engine.apply(
            Influence(type=InfluenceType.REMEMBER, primary_target="agent_1", reference="ghost")
        )

        assert result.success is False
        assert memory_manager.get_memories("agent_1") == []

    def test_remember_preserves_semantic_fields() -> None:
        """The resurfaced memory should keep all meaning-bearing fields,
        while receiving a fresh id and timestamp."""
        engine, memory_manager = _make_engine_with_agent()

        engine.apply(
            Influence(type=InfluenceType.REMEMBER, primary_target="agent_1", reference="mem_a")
        )

        original = memory_manager.get_memory("agent_1", "mem_a")
        resurfaced = next(m for m in memory_manager.get_memories("agent_1") if m.id != "mem_a")

        assert resurfaced.summary == original.summary
        assert resurfaced.subject_id == original.subject_id
        assert resurfaced.type == original.type
        assert resurfaced.source == original.source
        assert resurfaced.confidence == original.confidence
        assert resurfaced.id != original.id
        assert resurfaced.timestamp == 0.0

    def test_coincidence_duplicates_existing_memory() -> None:
        memory_manager = _make_memory_manager_with_memory("agent_1", "mem_a")
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        result = engine.apply(
            Influence(type=InfluenceType.COINCIDENCE, primary_target="agent_1", reference="mem_a")
        )

        assert result.success is True
        assert len(memory_manager.get_memories("agent_1")) == 2

    def test_coincidence_increases_confidence() -> None:
        """The resurfaced copy should have higher confidence than the original."""
        memory_manager = _make_memory_manager_with_memory("agent_1", "mem_a")
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        engine.apply(
            Influence(type=InfluenceType.COINCIDENCE, primary_target="agent_1", reference="mem_a")
        )

        original = memory_manager.get_memory("agent_1", "mem_a")
        resurfaced = next(m for m in memory_manager.get_memories("agent_1") if m.id != "mem_a")

        assert resurfaced.confidence > original.confidence
        assert resurfaced.confidence == min(original.confidence + 0.2, 1.0)

    def test_coincidence_confidence_caps_at_one() -> None:
        """Confidence boost should never exceed 1.0."""
        memory_manager = MemoryManager()
        memory_manager.add_memory(
            "agent_1",
            Memory(
                id="mem_high",
                summary="Definitely saw it happen.",
                type=MemoryType.WITNESS,
                source="self",
                timestamp=1.0,
                confidence=0.95,
            ),
        )
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        engine.apply(
            Influence(
                type=InfluenceType.COINCIDENCE, primary_target="agent_1", reference="mem_high"
            )
        )

        resurfaced = next(m for m in memory_manager.get_memories("agent_1") if m.id != "mem_high")
        assert resurfaced.confidence == 1.0

    def test_coincidence_new_copy_has_different_id() -> None:
        memory_manager = _make_memory_manager_with_memory("agent_1", "mem_a")
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        engine.apply(
            Influence(type=InfluenceType.COINCIDENCE, primary_target="agent_1", reference="mem_a")
        )

        ids = [m.id for m in memory_manager.get_memories("agent_1")]
        assert len(set(ids)) == 2

    def test_coincidence_preserves_semantic_fields() -> None:
        memory_manager = _make_memory_manager_with_memory("agent_1", "mem_a")
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        engine.apply(
            Influence(type=InfluenceType.COINCIDENCE, primary_target="agent_1", reference="mem_a")
        )

        original = memory_manager.get_memory("agent_1", "mem_a")
        resurfaced = next(m for m in memory_manager.get_memories("agent_1") if m.id != "mem_a")

        assert resurfaced.summary == original.summary
        assert resurfaced.subject_id == original.subject_id
        assert resurfaced.type == original.type
        assert resurfaced.source == original.source
        assert resurfaced.confidence == original.confidence
        assert resurfaced.timestamp == 0.0

    def test_coincidence_missing_reference_fails() -> None:
        memory_manager = MemoryManager()
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        result = engine.apply(Influence(type=InfluenceType.COINCIDENCE, primary_target="agent_1"))

        assert result.success is False
        assert memory_manager.get_memories("agent_1") == []

    def test_coincidence_unknown_memory_fails() -> None:
        memory_manager = MemoryManager()
        agent_manager = AgentManager()
        agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
        engine = HigherSelfEngine(memory_manager, agent_manager)

        result = engine.apply(
            Influence(type=InfluenceType.COINCIDENCE, primary_target="agent_1", reference="ghost")
        )

        assert result.success is False
        assert memory_manager.get_memories("agent_1") == []

    def test_warn_adds_one_memory() -> None:
        engine, memory_manager = _make_engine_with_agent()

        result = engine.apply(Influence(type=InfluenceType.WARN, primary_target="agent_1"))

        assert result.success is True
        assert result.affected_agents == ["agent_1"]
        assert len(memory_manager.get_memories("agent_1")) == 1

    def test_comfort_adds_one_memory() -> None:
        engine, memory_manager = _make_engine_with_agent()

        result = engine.apply(Influence(type=InfluenceType.COMFORT, primary_target="agent_1"))

        assert result.success is True
        assert len(memory_manager.get_memories("agent_1")) == 1

    def test_encourage_adds_one_memory() -> None:
        engine, memory_manager = _make_engine_with_agent()

        result = engine.apply(Influence(type=InfluenceType.ENCOURAGE, primary_target="agent_1"))

        assert result.success is True
        assert len(memory_manager.get_memories("agent_1")) == 1

    def test_warn_memory_has_no_subject_id() -> None:
        engine, memory_manager = _make_engine_with_agent()

        engine.apply(Influence(type=InfluenceType.WARN, primary_target="agent_1"))

        assert memory_manager.get_memories("agent_1")[0].subject_id is None
