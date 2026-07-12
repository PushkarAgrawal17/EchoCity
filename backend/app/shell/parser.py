"""Parses raw player input into Command objects."""

from app.shell.command import Command

_ARG_COUNTS: dict[str, tuple[int, int]] = {
    "help": (0, 0),
    "ls": (0, 0),
    "cd": (0, 1),
    "pwd": (0, 0),
    "tree": (0, 0),
    "observe": (0, 1),
    "question": (1, 1),
    "collect": (2, 2),
    "case": (0, 0),
    "remove": (1, 1),
    "clear": (0, 0),
    "accuse": (1, 1),
    "submit": (0, 0),
    "suggest": (1, 1),
    "warn": (1, 1),
    "comfort": (1, 1),
    "encourage": (1, 1),
    "remember": (2, 2),
    "coincidence": (2, 2),
}


class ParseError(Exception):
    """Raised when input cannot be parsed into a valid Command."""


class Parser:
    """Parses raw shell input into Command objects."""

    def parse(self, line: str) -> Command:
        """Parse one line of user input.

        Args:
            line: Raw input typed by the player.

        Returns:
            A validated Command.

        Raises:
            ParseError: If the command is unknown or has invalid arguments.
        """
        tokens = line.strip().split()
        if not tokens:
            raise ParseError("No command entered.")

        name, arguments = tokens[0], tuple(tokens[1:])

        if name not in _ARG_COUNTS:
            raise ParseError(f"Unknown command: '{name}'.")

        min_args, max_args = _ARG_COUNTS[name]
        if not (min_args <= len(arguments) <= max_args):
            raise ParseError(f"'{name}' expects between {min_args} and {max_args} argument(s).")

        return Command(name=name, arguments=arguments)
