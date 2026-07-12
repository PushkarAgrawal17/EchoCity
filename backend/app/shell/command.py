"""Defines the Command value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    """An immutable, parsed player command.

    Attributes:
        name: The command name (e.g. "cd", "observe").
        arguments: Positional arguments supplied with the command.
    """

    name: str
    arguments: tuple[str, ...] = ()
