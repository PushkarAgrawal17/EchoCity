"""Unit tests for app.simulation.world.World."""

from app.simulation.world import World


def test_world_starts_stopped_at_tick_zero() -> None:
    world = World()
    assert world.is_running is False
    assert world.tick_count == 0


def test_start_sets_running_true() -> None:
    world = World()
    world.start()
    assert world.is_running is True


def test_start_twice_is_idempotent() -> None:
    world = World()
    world.start()
    world.start()
    assert world.is_running is True


def test_stop_sets_running_false() -> None:
    world = World()
    world.start()
    world.stop()
    assert world.is_running is False


def test_stop_without_start_is_idempotent() -> None:
    world = World()
    world.stop()
    assert world.is_running is False


def test_tick_increments_count_when_running() -> None:
    world = World()
    world.start()
    world.tick()
    world.tick()
    assert world.tick_count == 2


def test_tick_does_nothing_when_not_running() -> None:
    world = World()
    world.tick()
    assert world.tick_count == 0


def test_tick_stops_incrementing_after_stop() -> None:
    world = World()
    world.start()
    world.tick()
    world.stop()
    world.tick()
    assert world.tick_count == 1