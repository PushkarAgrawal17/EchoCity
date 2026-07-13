"""EchoShell: virtual navigation and command dispatch over the simulation."""

from collections.abc import Callable
from typing import Any, cast

from app.court.case_file import CaseFile
from app.court.court_engine import CourtEngine
from app.court.evidence_manager import EvidenceManager
from app.higher_self.higher_self_engine import HigherSelfEngine
from app.higher_self.influence import Influence
from app.higher_self.influence_type import InfluenceType
from app.investigation.investigation_service import InvestigationService
from app.memory.memory import Memory
from app.shell.command import Command
from app.shell.parser import ParseError, Parser

_ROOT: dict[str, Any] = {
    "locations": {
        "court": {},
        "police_station": {},
        "cafe": {},
        "bank": {},
        "hospital": {},
        "school": {},
        "garage": {},
        "apartment_building": {},
        "park": {},
    },
}

_HELP_TEXT = (
    "Available commands:\n"
    "  help                               Show this message\n"
    "  man <command>                      Show detailed manual entry for a command\n"
    "  ls                                 List sub-locations\n"
    "  cd <target>                        Navigate locations\n"
    "  pwd                                Show current path\n"
    "  tree                               Show the location map\n"
    "  observe [location]                 List agents at a location\n"
    "  question <agent_id>                Question agent memories\n"
    "  collect <agent_id> <memory_index>  Collect evidence\n"
    "  case                               Show compiled evidence\n"
    "  remove <evidence_index>            Remove evidence from case file\n"
    "  clear                              Clear terminal screen\n"
    "  clear-case                         Clear evidence case file\n"
    "  accuse <agent_id>                  Accuse a suspect agent\n"
    "  submit                             Submit case to the Court\n"
    "  suggest / warn / comfort / encourage <agent_id> - Influence agent emotions\n"
    "  remember / coincidence <agent_id> <memory_index> - Influence agent thoughts\n"
    "  sim-start / resume / start         Resume background simulation ticks\n"
    "  sim-stop / pause                   Pause background simulation ticks\n"
    "  tick                               Manually advance simulation by one tick\n"
    "  sim-save                           Save current simulation state to SQLite\n"
    "  sim-status                         Show current clock and run status"
)


class Shell:
    """Reads, parses, and executes player commands.

    Owns navigation state (current path) as a purely presentational
    concept. Only 'observe' and 'question' reach into the simulation,
    via InvestigationService.
    """

    def __init__(
        self,
        world: Any,
        investigation_service: InvestigationService,
        evidence_manager: EvidenceManager,
        case_file: CaseFile,
        court_engine: CourtEngine,
        higher_self_engine: HigherSelfEngine,
    ) -> None:
        self._world = world
        self._investigation_service = investigation_service
        self._evidence_manager = evidence_manager
        self._case_file = case_file
        self._court_engine = court_engine
        self._higher_self_engine = higher_self_engine
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
            "man": self._cmd_man,
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "pwd": self._cmd_pwd,
            "tree": self._cmd_tree,
            "observe": self._cmd_observe,
            "question": self._cmd_question,
            "collect": self._cmd_collect,
            "case": self._cmd_case,
            "remove": self._cmd_remove,
            "clear-case": self._cmd_clear,
            "accuse": self._cmd_accuse,
            "submit": self._cmd_submit,
            "suggest": self._cmd_suggest,
            "warn": self._cmd_warn,
            "comfort": self._cmd_comfort,
            "encourage": self._cmd_encourage,
            "remember": self._cmd_remember,
            "coincidence": self._cmd_coincidence,
            "sim-start": self._cmd_sim_start,
            "sim-stop": self._cmd_sim_stop,
            "sim-status": self._cmd_sim_status,
            "sim-save": self._cmd_sim_save,
            "pause": self._cmd_sim_stop,
            "resume": self._cmd_sim_start,
            "start": self._cmd_sim_start,
            "tick": self._cmd_tick,
            "court.exe": self._cmd_court_exe,
            "cafe.exe": self._cmd_cafe_exe,
        }
        return handlers[command.name](command.arguments)

    def _current_node(self) -> dict[str, Any]:
        node: dict[str, Any] = cast(dict[str, Any], _ROOT["locations"])
        for segment in self._path:
            node = cast(dict[str, Any], node[segment])
        return node

    def _cmd_help(self, _arguments: tuple[str, ...]) -> str:
        return _HELP_TEXT

    def _cmd_man(self, arguments: tuple[str, ...]) -> str:
        if not arguments:
            return (
                "EchoShell Manual - Reference Guide\n"
                "Usage: man <command>\n\n"
                "Available commands to look up:\n"
                "  ls, cd, pwd, tree, observe, question, collect, case, remove, clear, accuse, submit, suggest, warn, comfort, encourage, remember, coincidence"
            )
        
        target = arguments[0].lower()
        manuals = {
            "help": "help\n  Displays the list of all available commands in EchoShell.",
            "man": "man <command>\n  Shows the detailed manual reference guide and usage for a specific command.",
            "ls": "ls\n  List entries (sub-locations) in your current location path.",
            "cd": "cd <target>\n  Change location path. Use 'cd ..' to move back, or 'cd /' to return to root.",
            "pwd": "pwd\n  Print current location path context.",
            "tree": "tree\n  Display the full hierarchical virtual map of EchoCity.",
            "observe": "observe [location]\n  Observe the target location and list all agents currently present there.",
            "question": "question <agent_id>\n  Question the target agent. Returns a numbered list of memories they recall.",
            "collect": "collect <agent_id> <memory_index>\n  Add a specific memory from an agent's testimony to the active case file.",
            "case": "case\n  Display all compiled evidence inside the active case file.",
            "remove": "remove <evidence_index>\n  Delete a piece of evidence from the active case file.",
            "clear": "clear\n  Clear the frontend terminal screen.",
            "clear-case": "clear-case\n  Clear all compiled evidence from the active case file.",
            "accuse": "accuse <agent_id>\n  Accuse a suspect of the active crime. Required before submitting a case to the Court.",
            "submit": "submit\n  Submit your compiled case file and accused suspect to the Court for final verdict evaluation.",
            "suggest": "suggest <agent_id>\n  Suggest a thought to influence the target agent.",
            "warn": "warn <agent_id>\n  Warn the target agent to influence their stress levels.",
            "comfort": "comfort <agent_id>\n  Comfort the target agent to reduce their stress levels.",
            "encourage": "encourage <agent_id>\n  Encourage the target agent to reinforce their active behaviors.",
            "remember": "remember <agent_id> <memory_index>\n  Force the target agent to remember a specific detail from their memory bank.",
            "coincidence": "coincidence <agent_id> <memory_index>\n  Influence the target agent's connection of events.",
            "sim-start": "sim-start\n  Starts the real-time simulation background tick loop.",
            "sim-stop": "sim-stop\n  Pauses the real-time simulation background tick loop.",
            "sim-status": "sim-status\n  Display the current simulation loop running status, active scene, tick count, and agent roster.",
            "sim-save": "sim-save\n  Save active simulation parameters and diaries to the SQLite database node.",
            "court.exe": "court.exe\n  Switches context to the Court Scene and resets steps to stage the trial sequence.",
            "cafe.exe": "cafe.exe\n  Switches context to the Cafe Scene and resets steps to stage the gossip sequence.",
        }
        
        return manuals.get(target, f"No manual entry found for command: '{target}'")

    def _cmd_sim_start(self, _arguments: tuple[str, ...]) -> str:
        if self._world.is_running:
            return "Simulation is already running."
        self._world.start()
        return "Simulation telemetry loop started."

    def _cmd_sim_stop(self, _arguments: tuple[str, ...]) -> str:
        if not self._world.is_running:
            return "Simulation is already stopped."
        self._world.stop()
        return "Simulation telemetry loop stopped / paused."

    def _cmd_sim_status(self, _arguments: tuple[str, ...]) -> str:
        status = "RUNNING" if self._world.is_running else "PAUSED"
        agents_count = len(list(self._world.agent_manager))
        events_count = len(self._world.narrative_events)
        
        return (
            f"=== EchoCity Observatory Status ===\n"
            f"Telemetry Node Loop : {status}\n"
            f"Simulation Clock   : Day {self._world.clock.day} - Tick {self._world.tick_count}\n"
            f"Active Scene       : {self._world.active_scene.upper()}\n"
            f"Scene Step         : {self._world.scene_step}\n"
            f"Registered Agents  : {agents_count} nodes\n"
            f"Narrative Log      : {events_count} events recorded\n"
            f"Local Databases    : ONLINE (SQLite persistent node)"
        )

    def _cmd_sim_save(self, _arguments: tuple[str, ...]) -> str:
        if hasattr(self._world, "db_repo") and self._world.db_repo:
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def run_sync(coro):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    return asyncio.run(coro)
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(lambda: asyncio.run(coro))
                    return future.result()
            run_sync(self._world.db_repo.save_world(self._world))

        return (
            f"Saving simulation telemetry state...\n"
            f"SQLite Transaction: COMMIT\n"
            f"Simulation state successfully committed to SQLite database node 'echocity.db'."
        )

    def _cmd_tick(self, _arguments: tuple[str, ...]) -> str:
        """Manually advance the simulation by one tick."""
        self._world.tick()
        if hasattr(self._world, "db_repo") and self._world.db_repo:
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def run_sync(coro):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    return asyncio.run(coro)
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(lambda: asyncio.run(coro))
                    return future.result()
            run_sync(self._world.db_repo.save_world(self._world))

        return f"Simulation advanced manually by one tick. Day: {self._world.clock.day}, Current Time: {self._world.clock.current_time}s"

    def _cmd_court_exe(self, _arguments: tuple[str, ...]) -> str:
        dialogue = self._world.run_full_court_scene()
        self._path = ["locations", "court"]
        return (
            "--- Command court.exe executed successfully. Simulation mode: COURT TRIAL ---\n\n"
            + dialogue
        )

    def _cmd_cafe_exe(self, _arguments: tuple[str, ...]) -> str:
        dialogue = self._world.run_full_cafe_scene()
        self._path = ["locations", "cafe"]
        return (
            "--- Command cafe.exe executed successfully. Simulation mode: CAFE GOSSIP ---\n\n"
            + dialogue
        )

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

        numbered_list = self._format_memories(memories)

        if getattr(self._world, "demo", True):
            return numbered_list

        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def run_sync(coro):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(coro)
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(lambda: asyncio.run(coro))
                return future.result()

        memories_summaries = [m.summary for m in memories]
        ai_dialogue = run_sync(self._world.brain_service.generate_question(agent_id, memories_summaries))

        return f"{agent.name} reacts: \"{ai_dialogue}\"\n\nRecollections:\n{numbered_list}"


    def _cmd_collect(self, arguments: tuple[str, ...]) -> str:
        agent_id, index_str = arguments

        result = self._resolve_memory(agent_id, index_str)
        if isinstance(result, str):
            return result

        evidence, created = self._evidence_manager.collect(result)
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
                f"You correctly identified {verdict.culprit_id}, " "but failed to prove the case."
            )
            lines.append(f"The Court acquits {verdict.culprit_id}.")
        else:
            lines.append("Correct.")
            lines.append(f"The Court convicts {verdict.culprit_id}.")

        return "\n".join(lines)

    def _cmd_suggest(self, arguments: tuple[str, ...]) -> str:
        agent_id = arguments[0]
        if self._investigation_service.get_agent(agent_id) is None:
            return f"No such agent: '{agent_id}'."
        result = self._higher_self_engine.apply(
            Influence(type=InfluenceType.SUGGEST, primary_target=agent_id)
        )
        return result.message

    def _cmd_warn(self, arguments: tuple[str, ...]) -> str:
        agent_id = arguments[0]
        if self._investigation_service.get_agent(agent_id) is None:
            return f"No such agent: '{agent_id}'."
        result = self._higher_self_engine.apply(
            Influence(type=InfluenceType.WARN, primary_target=agent_id)
        )
        return result.message

    def _cmd_comfort(self, arguments: tuple[str, ...]) -> str:
        agent_id = arguments[0]
        if self._investigation_service.get_agent(agent_id) is None:
            return f"No such agent: '{agent_id}'."
        result = self._higher_self_engine.apply(
            Influence(type=InfluenceType.COMFORT, primary_target=agent_id)
        )
        return result.message

    def _cmd_encourage(self, arguments: tuple[str, ...]) -> str:
        agent_id = arguments[0]
        if self._investigation_service.get_agent(agent_id) is None:
            return f"No such agent: '{agent_id}'."
        result = self._higher_self_engine.apply(
            Influence(type=InfluenceType.ENCOURAGE, primary_target=agent_id)
        )
        return result.message


    def _cmd_remember(self, arguments: tuple[str, ...]) -> str:
        agent_id, index_str = arguments

        if self._investigation_service.get_agent(agent_id) is None:
            return f"No such agent: '{agent_id}'."

        try:
            index = int(index_str)
        except ValueError:
            return "Invalid memory index."

        memories = self._investigation_service.get_agent_memories(agent_id)
        if not (1 <= index <= len(memories)):
            return "Memory not found."

        memory = memories[index - 1]
        result = self._higher_self_engine.apply(
            Influence(type=InfluenceType.REMEMBER, primary_target=agent_id, reference=memory.id)
        )
        return result.message

    def _cmd_coincidence(self, arguments: tuple[str, ...]) -> str:
        agent_id, index_str = arguments

        if self._investigation_service.get_agent(agent_id) is None:
            return f"No such agent: '{agent_id}'."

        try:
            index = int(index_str)
        except ValueError:
            return "Invalid memory index."

        memories = self._investigation_service.get_agent_memories(agent_id)
        if not (1 <= index <= len(memories)):
            return "Memory not found."

        memory = memories[index - 1]
        result = self._higher_self_engine.apply(
            Influence(type=InfluenceType.COINCIDENCE, primary_target=agent_id, reference=memory.id)
        )
        return result.message

    def _apply_simple_influence(self, agent_id: str, influence_type: InfluenceType) -> str:
        if self._investigation_service.get_agent(agent_id) is None:
            return f"No such agent: '{agent_id}'."
        result = self._higher_self_engine.apply(Influence(type=influence_type, primary_target=agent_id))
        if result.success and not getattr(self._world, "demo", True):
            memories = self._world.memory_manager.get_memories(agent_id)
            details = memories[-1].summary if memories else influence_type.name
            self._world.reasoning_queue.enqueue(
                lambda: self._world.brain_service.generate_influence(agent_id, influence_type.name, details)
            )
        return result.message

    def _apply_reference_influence(
        self, agent_id: str, index_str: str, influence_type: InfluenceType
    ) -> str:
        memory = self._resolve_memory(agent_id, index_str)
        if isinstance(memory, str):
            return memory
        result = self._higher_self_engine.apply(
            Influence(type=influence_type, primary_target=agent_id, reference=memory.id)
        )
        if result.success and not getattr(self._world, "demo", True):
            details = memory.summary
            self._world.reasoning_queue.enqueue(
                lambda: self._world.brain_service.generate_influence(agent_id, influence_type.name, details)
            )
        return result.message


    def _format_memories(self, memories: list[Memory]) -> str:
        """Format memories as plain, numbered text for display.

        Deterministic fallback formatter. An LLM-based formatter can
        later replace this call without touching dispatch. Indices here
        are 1-based and match what 'collect' expects.
        """
        if not memories:
            return ""
        return "\n".join(f"[{i}] {memory.summary}" for i, memory in enumerate(memories, start=1))


    def _resolve_memory(self, agent_id: str, index_str: str) -> Memory | str:
        """Resolve an agent_id + 1-based index into a Memory.

        Returns the Memory on success, or an error string on failure —
        callers should check the type before use.
        """
        if self._investigation_service.get_agent(agent_id) is None:
            return f"No such agent: '{agent_id}'."

        try:
            index = int(index_str)
        except ValueError:
            return "Invalid memory index."

        memories = self._investigation_service.get_agent_memories(agent_id)
        if not (1 <= index <= len(memories)):
            return "Memory not found."

        return memories[index - 1]