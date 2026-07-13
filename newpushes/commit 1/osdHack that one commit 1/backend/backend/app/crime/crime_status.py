"""Defines the resolution status of a Crime."""

from enum import Enum


class CrimeStatus(Enum):
    """Whether the crime has been solved by the player yet."""

    UNSOLVED = "unsolved"
    SOLVED = "solved"
