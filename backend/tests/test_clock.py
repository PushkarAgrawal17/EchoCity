"""Unit tests for app.simulation.clock.Clock."""

import pytest

from app.simulation.clock import Clock


def test_starts_at_zero() -> None:
    clock = Clock()
    assert clock.tick_count == 0
    assert clock.current_time == 0.0


def test_rejects_non_positive_tick_duration() -> None:
    with pytest.raises(ValueError):
        Clock(tick_duration_seconds=0)


def test_advance_increments_tick_count() -> None:
    clock = Clock()
    clock.advance()
    clock.advance()
    assert clock.tick_count == 2


def test_current_time_scales_with_tick_duration() -> None:
    clock = Clock(tick_duration_seconds=60.0)
    clock.advance()
    clock.advance()
    assert clock.current_time == 120.0


def test_reset_returns_to_zero() -> None:
    clock = Clock()
    clock.advance()
    clock.advance()
    clock.reset()
    assert clock.tick_count == 0
    assert clock.current_time == 0.0
