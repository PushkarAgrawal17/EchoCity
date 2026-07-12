"""Unit tests for app.simulation.simulation_engine.SimulationEngine."""

import pytest

from app.simulation.simulation_engine import SimulationEngine
from app.simulation.world import World


def test_rejects_non_positive_tick_interval() -> None:
    world = World()
    with pytest.raises(ValueError):
        SimulationEngine(world, tick_interval=0)


def test_start_starts_world() -> None:
    world = World()
    engine = SimulationEngine(world, sleep_fn=lambda _: None)
    engine.start()
    assert world.is_running is True


def test_stop_stops_world() -> None:
    world = World()
    engine = SimulationEngine(world, sleep_fn=lambda _: None)
    engine.start()
    engine.stop()
    assert world.is_running is False


def test_run_without_start_does_not_tick() -> None:
    world = World()
    engine = SimulationEngine(world, sleep_fn=lambda _: None)
    engine.run()
    assert world.tick_count == 0


def test_run_ticks_world_each_loop_iteration() -> None:
    world = World()
    tick_target = 3
    calls = {"count": 0}

    def fake_sleep(_: float) -> None:
        calls["count"] += 1
        if calls["count"] > tick_target:
            engine.stop()

    engine = SimulationEngine(world, sleep_fn=fake_sleep)
    engine.start()
    engine.run()

    assert world.tick_count == tick_target


def test_run_uses_configured_tick_interval() -> None:
    world = World()
    recorded_intervals = []

    def fake_sleep(interval: float) -> None:
        recorded_intervals.append(interval)
        engine.stop()

    engine = SimulationEngine(world, tick_interval=0.25, sleep_fn=fake_sleep)
    engine.start()
    engine.run()

    assert recorded_intervals == [0.25]
