"""Unit tests for app.simulation.scheduler.Scheduler."""

import pytest

from app.simulation.clock import Clock
from app.simulation.scheduler import Scheduler


def make_scheduler(tick_duration: float = 1.0) -> tuple[Scheduler, Clock]:
    clock = Clock(tick_duration_seconds=tick_duration)
    return Scheduler(clock), clock


def test_task_not_run_before_due() -> None:
    scheduler, clock = make_scheduler()
    calls = []
    scheduler.schedule_at(10.0, lambda: calls.append(1))

    scheduler.run_due_tasks()  # current_time == 0

    assert calls == []


def test_task_runs_when_due() -> None:
    scheduler, clock = make_scheduler()
    calls = []
    scheduler.schedule_at(0.0, lambda: calls.append(1))

    scheduler.run_due_tasks()

    assert calls == [1]


def test_one_shot_task_removed_after_running() -> None:
    scheduler, clock = make_scheduler()
    calls = []
    scheduler.schedule_at(0.0, lambda: calls.append(1))

    scheduler.run_due_tasks()
    scheduler.run_due_tasks()

    assert calls == [1]


def test_tasks_run_in_time_order() -> None:
    scheduler, clock = make_scheduler()
    order = []
    scheduler.schedule_at(2.0, lambda: order.append("second"))
    scheduler.schedule_at(1.0, lambda: order.append("first"))

    clock.advance()
    clock.advance()  # current_time == 2.0
    scheduler.run_due_tasks()

    assert order == ["first", "second"]


def test_same_time_tasks_run_in_schedule_order() -> None:
    scheduler, clock = make_scheduler()
    order = []
    scheduler.schedule_at(0.0, lambda: order.append("a"))
    scheduler.schedule_at(0.0, lambda: order.append("b"))
    scheduler.schedule_at(0.0, lambda: order.append("c"))

    scheduler.run_due_tasks()

    assert order == ["a", "b", "c"]


def test_repeating_task_reschedules_after_running() -> None:
    scheduler, clock = make_scheduler()
    calls = []
    scheduler.schedule_at(0.0, lambda: calls.append(clock.current_time), interval=5.0)

    scheduler.run_due_tasks()  # runs at t=0, reschedules for t=5
    assert calls == [0.0]

    scheduler.run_due_tasks()  # still t=0, not due again
    assert calls == [0.0]

    for _ in range(5):
        clock.advance()  # t=5.0
    scheduler.run_due_tasks()

    assert calls == [0.0, 5.0]


def test_repeating_task_catches_up_within_one_call() -> None:
    """A single run_due_tasks() call executes every occurrence that has
    become due, even if several intervals passed at once (e.g. after a
    large time jump): occurrences due at 0, 5, and 10 all fire once
    execution reaches t=12."""
    scheduler, clock = make_scheduler()
    call_count = [0]
    scheduler.schedule_at(0.0, lambda: call_count.__setitem__(0, call_count[0] + 1), interval=5.0)

    for _ in range(12):
        clock.advance()  # t=12.0
    scheduler.run_due_tasks()

    assert call_count[0] == 3  # occurrences at t=0, 5, 10


def test_repeating_task_cadence_anchored_to_run_at_not_exec_time() -> None:
    """After catching up to t=12 (occurrences at 0, 5, 10 consumed), the
    next occurrence must be anchored at 15 (10 + interval), not at
    12 + interval — i.e. it should NOT be due yet at t=14."""
    scheduler, clock = make_scheduler()
    call_count = [0]
    scheduler.schedule_at(0.0, lambda: call_count.__setitem__(0, call_count[0] + 1), interval=5.0)

    for _ in range(12):
        clock.advance()  # t=12.0
    scheduler.run_due_tasks()
    assert call_count[0] == 3

    for _ in range(2):
        clock.advance()  # t=14.0
    scheduler.run_due_tasks()
    assert call_count[0] == 3  # not due yet — next occurrence is at t=15

    clock.advance()  # t=15.0
    scheduler.run_due_tasks()
    assert call_count[0] == 4  # now due


def test_rejects_non_positive_interval() -> None:
    scheduler, _ = make_scheduler()
    with pytest.raises(ValueError):
        scheduler.schedule_at(0.0, lambda: None, interval=0)
