"""Scheduler: executes tasks at scheduled simulation time.

Depends only on Clock. Has no knowledge of World, SimulationEngine,
Agents, Events, or AI — it just knows "what time is it" (via Clock) and
"what callables are due."
"""

import heapq
import itertools
from collections.abc import Callable
from dataclasses import dataclass, field

from app.simulation.clock import Clock

Task = Callable[[], None]


@dataclass(order=True)
class _ScheduledTask:
    """Internal heap entry. Ordered by (run_at, sequence) only.

    ``sequence`` breaks ties between tasks scheduled for the same
    ``run_at``, in the order ``schedule_at`` was called (FIFO).
    """

    run_at: float
    sequence: int
    task: Task = field(compare=False)
    interval: float | None = field(compare=False)


class Scheduler:
    """Schedules and executes callables against simulation time.

    Tasks are plain callables taking no arguments. A task may be one-shot
    (executed once, then discarded) or repeating (rescheduled ``interval``
    simulation-seconds after its current ``run_at`` each time it runs).

    Attributes:
        clock: The Clock used to determine which tasks are due.
    """

    def __init__(self, clock: Clock) -> None:
        """Create a Scheduler bound to a Clock.

        Args:
            clock: The Clock whose ``current_time`` determines due tasks.
        """
        self.clock = clock
        self._heap: list[_ScheduledTask] = []
        self._sequence_counter = itertools.count()

    def schedule_at(self, run_at: float, task: Task, interval: float | None = None) -> None:
        """Schedule ``task`` to run at simulation time ``run_at``.

        Args:
            run_at: Simulation time (in the same units as
                ``clock.current_time``) at which the task becomes due.
            task: A zero-argument callable to execute when due.
            interval: If given, the task repeats: after each execution it
                is rescheduled for ``run_at + interval`` (using its
                previous ``run_at``, not the current time — so a repeating
                task's cadence does not drift based on when it happens to
                be executed). Must be positive if provided.

        Raises:
            ValueError: If ``interval`` is provided and not positive.
        """
        if interval is not None and interval <= 0:
            raise ValueError("interval must be positive.")

        entry = _ScheduledTask(
            run_at=run_at,
            sequence=next(self._sequence_counter),
            task=task,
            interval=interval,
        )
        self._insert(entry)

    def run_due_tasks(self) -> None:
        """Execute every task whose ``run_at`` has arrived.

        A task is due when ``run_at <= clock.current_time``. Due tasks run
        in ``(run_at, schedule order)`` order. One-shot tasks are removed
        after running; repeating tasks are rescheduled for
        ``run_at + interval``.
        """
        now = self.clock.current_time

        while self._heap and self._heap[0].run_at <= now:
            entry = self._pop()
            entry.task()

            if entry.interval is not None:
                self.schedule_at(entry.run_at + entry.interval, entry.task, entry.interval)

    def _insert(self, entry: _ScheduledTask) -> None:
        heapq.heappush(self._heap, entry)

    def _pop(self) -> _ScheduledTask:
        return heapq.heappop(self._heap)
