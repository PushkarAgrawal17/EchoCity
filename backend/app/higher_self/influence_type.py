"""Defines the kinds of intent the Higher Self can express."""

from enum import Enum


class InfluenceType(Enum):
    """Classifies the player's intent when influencing a citizen.

    SUGGEST: Plant a vague suspicion or idea.
    REMEMBER: Resurface something the citizen already knows.
    WARN: Instill a sense of danger or caution.
    COMFORT: Instill reassurance.
    ENCOURAGE: Instill a positive expectation.
    CONNECT: Draw two citizens' attention toward each other.
    COINCIDENCE: Trigger a spontaneous realization.
    """

    SUGGEST = "suggest"
    REMEMBER = "remember"
    WARN = "warn"
    COMFORT = "comfort"
    ENCOURAGE = "encourage"
    CONNECT = "connect"
    COINCIDENCE = "coincidence"
