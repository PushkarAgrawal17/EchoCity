"""EchoShell: virtual navigation and command dispatch over the simulation."""

from collections.abc import Callable
from typing import Any, cast

from app.court.case_file import CaseFile
from app.court.court_engine import CourtEngine
from app.court.evidence_manager import EvidenceManager
from app.investigation.investigation_service import InvestigationService
from app.memory.memory import Memory
from app.shell.command import Command
from app.shell.parser import ParseError, Parser

_ROOT: dict[str, Any] = {
    "locations": {
        "cafe": {},
        "court": {},
    },
}

_HELP_TEXT = (
    "Available commands:\n"
    "  help                 Show this message\n"
    "  ls                   List entries in the current location\n"
    "  cd <target>          Move to a location ('cd ..' or 'cd /' to go back)\n"
    "  pwd                  Show current path\n"
    "  tree                 Show the full virtual map\n"
    "  observe [location]   List agents present at a location\n"
    "  question <agent_id>  Ask an agent what they remember"
)


class Shell:
    """Reads, parses, and executes player commands.

    Owns navigation state (current path) as a purely presentational
    concept. Only 'observe' and 'question' reach into the simulation,
    via InvestigationService.
    """

    def __init__(
        self,
        investigation_service: InvestigationService,
        evidence_manager: EvidenceManager,
        case_file: CaseFile,
        court_engine: CourtEngine,
    ) -> None:
        """Create a Shell bound to backend services."""
        self._investigation_service = investigation_service
        self._evidence_manager = evidence_manager
        self._case_file = case_file
        self._court_engine = court_engine
        self._parser = Parser()
        self._path: list[str] = []
        self._accusation: str | None = None


    def execute_line(self, line: str) -> str:
        """Parse and execute one line of input.

        Args:
            line: Raw input typed by the player.

        Returns:
            The text output to display to the player.
        """
        try:
            command = self._parser.parse(line)
        except ParseError as error:
            return str(error)

        return self._dispatch(command)


    def _dispatch(self, command: Command) -> str:
        handlers: dict[str, Callable[[tuple[str, ...]], str]] = {
            "help": self._cmd_help,
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "pwd": self._cmd_pwd,
            "tree": self._cmd_tree,
            "observe": self._cmd_observe,
            "question": self._cmd_question,
            "collect": self._cmd_collect,
            "case": self._cmd_case,
            "remove": self._cmd_remove,
            "clear": self._cmd_clear,
            "accuse": self._cmd_accuse,
            "submit": self._cmd_submit,
        }
        return handlers[command.name](command.arguments)


    def _current_node(self) -> dict[str, Any]:
        node: dict[str, Any] = cast(dict[str, Any], _ROOT["locations"])
        for segment in self._path:
            node = cast(dict[str, Any], node[segment])
        return node


    def _cmd_help(self, _arguments: tuple[str, ...]) -> str:
        return _HELP_TEXT


    def _cmd_pwd(self, _arguments: tuple[str, ...]) -> str:
        return "/" + "/".join(self._path)


    def _cmd_ls(self, _arguments: tuple[str, ...]) -> str:
        children = list(self._current_node().keys())
        return "\n".join(children) if children else "(empty)"


    def _cmd_tree(self, _arguments: tuple[str, ...]) -> str:
        lines = ["/"] + [f"  {name}" for name in _ROOT["locations"]]
        return "\n".join(lines)


    def _cmd_cd(self, arguments: tuple[str, ...]) -> str:
        if not arguments or arguments[0] == "/":
            self._path = []
            return self._cmd_pwd(())

        target = arguments[0]
        if target == "..":
            if self._path:
                self._path.pop()
            return self._cmd_pwd(())

        node = self._current_node()
        if target not in node:
            return f"No such location: '{target}'."

        self._path.append(target)
        return self._cmd_pwd(())


    def _cmd_observe(self, arguments: tuple[str, ...]) -> str:
        location_id = arguments[0] if arguments else (self._path[-1] if self._path else None)
        if location_id is None:
            return "You are not in a location. Use 'cd <location>' or 'observe <location>'."

        agents = self._investigation_service.observe_location(location_id)
        if not agents:
            return f"No one is at '{location_id}'."
        return "\n".join(agent.agent_id for agent in agents)


    def _cmd_question(self, arguments: tuple[str, ...]) -> str:
        agent_id = arguments[0]
        agent = self._investigation_service.get_agent(agent_id)
        if agent is None:
            return f"No such agent: '{agent_id}'."

        memories = self._investigation_service.get_agent_memories(agent_id)
        if not memories:
            return f"{agent_id} has nothing to say."
        return self._format_memories(memories)


    def _cmd_collect(self, arguments: tuple[str, ...]) -> str:
        agent_id, index_str = arguments

        agent = self._investigation_service.get_agent(agent_id)
        if agent is None:
            return f"No such agent: '{agent_id}'."

        try:
            index = int(index_str)
        except ValueError:
            return "Invalid memory index."

        memories = self._investigation_service.get_agent_memories(agent_id)
        if not (1 <= index <= len(memories)):
            return "Memory not found."

        memory = memories[index - 1]
        evidence, created = self._evidence_manager.collect(memory)

        self._case_file.add_evidence(evidence)

        return "Evidence collected." if created else "Evidence already collected."


    def _cmd_case(self, _arguments: tuple[str, ...]) -> str:
        evidence_list = self._case_file.list_evidence()
        if not evidence_list:
            return "Case file is empty."
        return "\n".join(
            f"[{i}] {evidence.memory.summary}" for i, evidence in enumerate(evidence_list, start=1)
        )


    def _cmd_remove(self, arguments: tuple[str, ...]) -> str:
        try:
            index = int(arguments[0])
        except ValueError:
            return "Invalid evidence index."

        evidence_list = self._case_file.list_evidence()
        if not (1 <= index <= len(evidence_list)):
            return "Invalid evidence index."

        self._case_file.remove_evidence(evidence_list[index - 1].id)
        return "Evidence removed."


    def _cmd_clear(self, _arguments: tuple[str, ...]) -> str:
        if not self._case_file.list_evidence():
            return "Case file already empty."
        self._case_file.clear()
        return "Case file cleared."


    def _cmd_accuse(self, arguments: tuple[str, ...]) -> str:
        agent_id = arguments[0]
        if self._investigation_service.get_agent(agent_id) is None:
            return f"No such agent: '{agent_id}'."

        self._accusation = agent_id
        return f"You accuse '{agent_id}'."


    def _cmd_submit(self, _arguments: tuple[str, ...]) -> str:
        if self._accusation is None:
            return "You have not accused anyone yet."

        verdict = self._court_engine.evaluate(self._case_file)
        accused_correctly = self._accusation == verdict.culprit_id

        lines = [f"You accused '{self._accusation}'.", "Verdict:"]

        if not accused_correctly:
            lines.append("Incorrect.")
            lines.append(f"The true culprit was {verdict.culprit_id}.")
        elif not verdict.success:
            lines.append("Insufficient evidence.")
            lines.append(
                f"You correctly identified {verdict.culprit_id}, "
                "but failed to prove the case."
            )
            lines.append(f"The Court acquits {verdict.culprit_id}.")
        else:
            lines.append("Correct.")
            lines.append(f"The Court convicts {verdict.culprit_id}.")

        return "\n".join(lines)


    def _format_memories(self, memories: list[Memory]) -> str:
        """Format memories as plain, numbered text for display.

        Deterministic fallback formatter. An LLM-based formatter can
        later replace this call without touching dispatch. Indices here
        are 1-based and match what 'collect' expects.
        """
        if not memories:
            return ""
        return "\n".join(f"[{i}] {memory.summary}" for i, memory in enumerate(memories, start=1))