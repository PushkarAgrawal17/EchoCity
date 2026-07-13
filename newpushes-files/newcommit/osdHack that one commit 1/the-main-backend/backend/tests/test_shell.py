"""Tests for Shell."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.agents.agent import Agent
from app.agents.agent_manager import AgentManager
from app.court.case_file import CaseFile
from app.court.court_engine import CourtEngine
from app.court.evidence_manager import EvidenceManager
from app.crime.crime_engine import CrimeEngine
from app.higher_self.higher_self_engine import HigherSelfEngine
from app.investigation.investigation_service import InvestigationService
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType
from app.shell.shell import Shell


def _make_shell() -> tuple[Shell, MagicMock]:
    service = MagicMock(spec=InvestigationService)
    evidence_manager = EvidenceManager()
    case_file = CaseFile()
    crime_engine = CrimeEngine(MemoryManager())
    crime_engine.create_crime()
    court_engine = CourtEngine(crime_engine)

    agent_manager = AgentManager()
    memory_manager = MemoryManager()
    higher_self_engine = HigherSelfEngine(memory_manager, agent_manager)

    world = MagicMock()
    shell = Shell(world, service, evidence_manager, case_file, court_engine, higher_self_engine)
    return shell, service


def make_memory(memory_id: str) -> Memory:
    return Memory(
        id=memory_id, summary="Saw something.", type=MemoryType.WITNESS,
        source="self", timestamp=0.0, confidence=0.9,
    )


def _make_shell_with_higher_self() -> tuple[Shell, MagicMock, AgentManager, MemoryManager]:
    """Build a Shell wired with a real HigherSelfEngine, for Higher Self
    command tests that need to verify actual memory-manager state."""
    service = MagicMock(spec=InvestigationService)
    evidence_manager = EvidenceManager()
    case_file = CaseFile()
    crime_engine = CrimeEngine(MemoryManager())
    crime_engine.create_crime()
    court_engine = CourtEngine(crime_engine)

    agent_manager = AgentManager()
    memory_manager = MemoryManager()
    higher_self_engine = HigherSelfEngine(memory_manager, agent_manager)

    world = MagicMock()
    shell = Shell(world, service, evidence_manager, case_file, court_engine, higher_self_engine)
    return shell, service, agent_manager, memory_manager


def test_pwd_starts_at_root() -> None:
    shell, _ = _make_shell()
    assert shell.execute_line("pwd") == "/"


def test_cd_into_known_location() -> None:
    shell, _ = _make_shell()
    assert shell.execute_line("cd cafe") == "/cafe"
    assert shell.execute_line("pwd") == "/cafe"


def test_cd_into_unknown_location() -> None:
    shell, _ = _make_shell()
    result = shell.execute_line("cd nowhere")
    assert "No such location" in result


def test_cd_dotdot_returns_to_root() -> None:
    shell, _ = _make_shell()
    shell.execute_line("cd cafe")
    assert shell.execute_line("cd ..") == "/"


def test_ls_lists_locations_at_root() -> None:
    shell, _ = _make_shell()
    result = shell.execute_line("ls")
    assert "cafe" in result
    assert "court" in result


def test_observe_uses_current_location() -> None:
    shell, service = _make_shell()

    agent = SimpleNamespace(agent_id="agent_3")
    service.observe_location.return_value = [agent]

    shell.execute_line("cd cafe")
    result = shell.execute_line("observe")

    service.observe_location.assert_called_once_with("cafe")
    assert result == "agent_3"


def test_observe_outside_location_without_argument() -> None:
    shell, _ = _make_shell()
    result = shell.execute_line("observe")
    assert "not in a location" in result


def test_question_unknown_agent() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = None

    result = shell.execute_line("question agent_99")

    assert "No such agent" in result


def test_question_returns_memory_summaries() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()
    memory = MagicMock()
    memory.summary = "Saw something suspicious."
    service.get_agent_memories.return_value = [memory]

    result = shell.execute_line("question agent_3")

    assert "[1]" in result
    assert "Saw something suspicious." in result


def test_invalid_command_returns_error_message() -> None:
    shell, _ = _make_shell()
    result = shell.execute_line("fly")
    assert "Unknown command" in result


def test_question_shows_numbered_memories() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()
    m1, m2 = MagicMock(), MagicMock()
    m1.summary = "Saw Noah leave."
    m2.summary = "Heard Victor arguing."
    service.get_agent_memories.return_value = [m1, m2]

    result = shell.execute_line("question emma")

    assert result == "[1] Saw Noah leave.\n[2] Heard Victor arguing."


def test_collect_unknown_agent() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = None

    result = shell.execute_line("collect emma 1")

    assert "No such agent" in result


def test_collect_invalid_index_format() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()

    result = shell.execute_line("collect emma abc")

    assert result == "Invalid memory index."


def test_collect_index_out_of_range() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()
    service.get_agent_memories.return_value = []

    result = shell.execute_line("collect emma 1")

    assert result == "Memory not found."


def test_collect_success() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()
    memory = MagicMock()
    memory.id = "mem_1"
    service.get_agent_memories.return_value = [memory]

    result = shell.execute_line("collect emma 1")

    assert result == "Evidence collected."


def test_collect_duplicate() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()
    memory = MagicMock()
    memory.id = "mem_1"
    service.get_agent_memories.return_value = [memory]

    shell.execute_line("collect emma 1")
    result = shell.execute_line("collect emma 1")

    assert result == "Evidence already collected."


def test_case_empty() -> None:
    shell, _ = _make_shell()
    assert shell.execute_line("case") == "Case file is empty."


def test_collect_adds_to_case_file() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()
    memory = MagicMock()
    memory.id = "mem_1"
    memory.summary = "Saw Noah leave the cafe."
    service.get_agent_memories.return_value = [memory]

    shell.execute_line("collect emma 1")
    result = shell.execute_line("case")

    assert result == "[1] Saw Noah leave the cafe."


def test_remove_valid_index() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()
    memory = MagicMock()
    memory.id = "mem_1"
    memory.summary = "Saw Noah leave."
    service.get_agent_memories.return_value = [memory]

    shell.execute_line("collect emma 1")
    result = shell.execute_line("remove 1")

    assert result == "Evidence removed."
    assert shell.execute_line("case") == "Case file is empty."


def test_remove_invalid_index() -> None:
    shell, _ = _make_shell()
    result = shell.execute_line("remove 1")
    assert result == "Invalid evidence index."


def test_remove_non_numeric_index() -> None:
    shell, _ = _make_shell()
    result = shell.execute_line("remove abc")
    assert result == "Invalid evidence index."


def test_clear_empty() -> None:
    shell, _ = _make_shell()
    assert shell.execute_line("clear-case") == "Case file already empty."


def test_clear_removes_all() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()
    memory = MagicMock()
    memory.id = "mem_1"
    memory.summary = "Saw Noah leave."
    service.get_agent_memories.return_value = [memory]

    shell.execute_line("collect emma 1")
    result = shell.execute_line("clear-case")

    assert result == "Case file cleared."
    assert shell.execute_line("case") == "Case file is empty."


def test_remove_does_not_affect_evidence_manager() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()
    memory = MagicMock()
    memory.id = "mem_1"
    memory.summary = "Saw Noah leave."
    service.get_agent_memories.return_value = [memory]

    shell.execute_line("collect emma 1")
    shell.execute_line("remove 1")
    result = shell.execute_line("collect emma 1")

    assert result == "Evidence already collected."


def test_accuse_unknown_agent() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = None

    result = shell.execute_line("accuse agent_99")

    assert result == "No such agent: 'agent_99'."


def test_accuse_known_agent() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()

    result = shell.execute_line("accuse agent_2")

    assert result == "You accuse 'agent_2'."


def test_submit_without_accusation() -> None:
    shell, _ = _make_shell()
    result = shell.execute_line("submit")
    assert result == "You have not accused anyone yet."


def test_submit_incorrect_culprit() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()

    shell.execute_line("accuse agent_3")  # true culprit is agent_2
    result = shell.execute_line("submit")

    assert "Incorrect." in result
    assert "agent_2" in result


def test_submit_correct_culprit_but_insufficient_evidence() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()

    shell.execute_line("accuse agent_2")  # correct culprit, empty case file
    result = shell.execute_line("submit")

    assert "Insufficient evidence." in result
    assert "acquits agent_2" in result


def test_submit_correct_culprit_with_sufficient_evidence() -> None:
    shell, service = _make_shell()
    service.get_agent.return_value = MagicMock()

    memory1, memory2 = MagicMock(), MagicMock()
    memory1.id, memory1.subject_id, memory1.summary = "m1", "agent_2", "s1"
    memory2.id, memory2.subject_id, memory2.summary = "m2", "agent_2", "s2"
    service.get_agent_memories.return_value = [memory1, memory2]

    shell.execute_line("collect emma 1")
    shell.execute_line("collect emma 2")
    shell.execute_line("accuse agent_2")
    result = shell.execute_line("submit")

    assert "Correct." in result
    assert "convicts agent_2" in result


def test_suggest_unknown_agent() -> None:
    shell, service, _, _ = _make_shell_with_higher_self()
    service.get_agent.return_value = None

    result = shell.execute_line("suggest agent_99")

    assert result == "No such agent: 'agent_99'."


def test_suggest_success_adds_memory() -> None:
    shell, service, agent_manager, memory_manager = _make_shell_with_higher_self()
    service.get_agent.return_value = MagicMock()
    agent_manager.register(Agent(agent_id="agent_3", name="Agent Three"))

    result = shell.execute_line("suggest agent_3")

    assert result == "A subtle influence has taken hold."
    assert len(memory_manager.get_memories("agent_3")) == 1


def test_warn_success_adds_memory() -> None:
    shell, service, agent_manager, memory_manager = _make_shell_with_higher_self()
    service.get_agent.return_value = MagicMock()
    agent_manager.register(Agent(agent_id="agent_3", name="Agent Three"))
    shell.execute_line("warn agent_3")
    assert len(memory_manager.get_memories("agent_3")) == 1


def test_comfort_unknown_agent() -> None:
    shell, service, _, _ = _make_shell_with_higher_self()
    service.get_agent.return_value = None
    assert shell.execute_line("comfort agent_99") == "No such agent: 'agent_99'."


def test_encourage_success_adds_memory() -> None:
    shell, service, agent_manager, memory_manager = _make_shell_with_higher_self()
    service.get_agent.return_value = MagicMock()
    agent_manager.register(Agent(agent_id="agent_3", name="Agent Three"))
    shell.execute_line("encourage agent_3")
    assert len(memory_manager.get_memories("agent_3")) == 1


def test_remember_unknown_agent() -> None:
    shell, service, _, _ = _make_shell_with_higher_self()
    service.get_agent.return_value = None
    assert shell.execute_line("remember agent_99 1") == "No such agent: 'agent_99'."


def test_remember_index_out_of_range() -> None:
    shell, service, agent_manager, _ = _make_shell_with_higher_self()
    service.get_agent.return_value = MagicMock()
    service.get_agent_memories.return_value = []
    agent_manager.register(Agent(agent_id="agent_3", name="Agent Three"))
    assert shell.execute_line("remember agent_3 1") == "Memory not found."


def test_remember_success_duplicates_memory() -> None:
    shell, service, agent_manager, memory_manager = _make_shell_with_higher_self()
    agent_manager.register(Agent(agent_id="agent_3", name="Agent Three"))
    memory_manager.add_memory("agent_3", make_memory("mem_x"))
    service.get_agent.return_value = MagicMock()
    service.get_agent_memories.return_value = memory_manager.get_memories("agent_3")
    shell.execute_line("remember agent_3 1")
    assert len(memory_manager.get_memories("agent_3")) == 2


def test_coincidence_index_out_of_range() -> None:
    shell, service, agent_manager, _ = _make_shell_with_higher_self()
    service.get_agent.return_value = MagicMock()
    service.get_agent_memories.return_value = []
    agent_manager.register(Agent(agent_id="agent_3", name="Agent Three"))
    assert shell.execute_line("coincidence agent_3 1") == "Memory not found."


def test_coincidence_success_duplicates_memory() -> None:
    shell, service, agent_manager, memory_manager = _make_shell_with_higher_self()
    agent_manager.register(Agent(agent_id="agent_3", name="Agent Three"))
    memory_manager.add_memory("agent_3", make_memory("mem_x"))
    service.get_agent.return_value = MagicMock()
    service.get_agent_memories.return_value = memory_manager.get_memories("agent_3")
    shell.execute_line("coincidence agent_3 1")
    assert len(memory_manager.get_memories("agent_3")) == 2