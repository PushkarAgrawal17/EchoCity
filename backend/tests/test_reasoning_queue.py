"""Unit tests for the priority-ordered, cancellable ReasoningQueue."""

import asyncio
import pytest
from app.llm.queue import ReasoningQueue


@pytest.mark.asyncio
async def test_queue_concurrency_limit() -> None:
    queue = ReasoningQueue(max_concurrency=2)
    active_count = 0
    max_observed = 0

    async def mock_task() -> None:
        nonlocal active_count, max_observed
        active_count += 1
        max_observed = max(max_observed, active_count)
        await asyncio.sleep(0.05)
        active_count -= 1

    # Enqueue 5 tasks
    for _ in range(5):
        queue.enqueue(mock_task)

    await queue.wait_until_idle()
    await queue.shutdown()

    # Max concurrency should be capped at 2
    assert max_observed <= 2


@pytest.mark.asyncio
async def test_queue_priority_ordering() -> None:
    queue = ReasoningQueue(max_concurrency=1)  # Concurrency = 1 to enforce sequence
    execution_order = []

    # Enqueue first task to block the worker
    block_evt = asyncio.Event()

    async def blocking_task() -> None:
        await block_evt.wait()

    queue.enqueue(blocking_task, priority=2)

    # Enqueue tasks with different priorities
    async def task_low() -> None:
        execution_order.append("low")

    async def task_high() -> None:
        execution_order.append("high")

    async def task_immediate() -> None:
        execution_order.append("immediate")

    # Enqueued in reverse priority order
    queue.enqueue(task_low, priority=3)
    queue.enqueue(task_high, priority=1)
    queue.enqueue(task_immediate, priority=0)

    # Release worker
    block_evt.set()

    await queue.wait_until_idle()
    await queue.shutdown()

    # The order of execution should be immediate, high, low
    assert execution_order == ["immediate", "high", "low"]


@pytest.mark.asyncio
async def test_queue_cancellation_pre_run() -> None:
    queue = ReasoningQueue(max_concurrency=1)
    run_log = []

    # Block the queue
    block_evt = asyncio.Event()
    queue.enqueue(block_evt.wait, priority=0)

    # Enqueue task to cancel
    async def cancel_me() -> None:
        run_log.append("run")

    req_id = queue.enqueue(cancel_me, priority=1)
    
    # Cancel it
    canceled = queue.cancel(req_id)
    assert canceled is True

    # Unblock
    block_evt.set()

    await queue.wait_until_idle()
    await queue.shutdown()

    # Should not have run
    assert "run" not in run_log


@pytest.mark.asyncio
async def test_queue_retries_on_failure() -> None:
    queue = ReasoningQueue(max_concurrency=1)
    attempts = 0

    async def failing_task() -> None:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Ollama Timeout")
        # Succeeds on 3rd attempt

    queue.enqueue(failing_task, retries=3)

    await queue.wait_until_idle()
    await queue.shutdown()

    # It should have run 3 times total
    assert attempts == 3
