"""Unit tests for the EventManager routing subsystem."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.events.event import Event
from app.events.event_type import EventType
from app.events.event_manager import EventManager
from app.llm.queue import ReasoningQueue


def test_event_manager_non_cognitive_immediate_update() -> None:
    # Set up mocks
    queue_mock = MagicMock(spec=ReasoningQueue)
    manager = EventManager(queue_mock)
    
    # Track handler execution
    handler_called = False
    received_event = None
    
    def dummy_handler(event: Event) -> None:
        nonlocal handler_called, received_event
        handler_called = True
        received_event = event
        
    manager.register_handler(EventType.AGENT_REGISTERED, dummy_handler)
    
    event = Event(
        event_type=EventType.AGENT_REGISTERED,
        timestamp=100.0,
        payload={"agent_id": "test_agent"}
    )
    
    # Process event
    manager.handle_event(event)
    
    # Verify handler ran immediately and LLM queue was ignored
    assert handler_called == True
    assert received_event == event
    queue_mock.enqueue.assert_not_called()


@pytest.mark.asyncio
async def test_event_manager_cognitive_queues_task() -> None:
    queue_mock = MagicMock(spec=ReasoningQueue)
    queue_mock.enqueue.return_value = "req_123"
    
    manager = EventManager(queue_mock)
    
    # We do NOT expect handler to run
    handler_called = False
    def dummy_handler(event: Event) -> None:
        nonlocal handler_called
        handler_called = True
        
    manager.register_handler(EventType.CONVERSATION_STARTED, dummy_handler)
    
    event = Event(
        event_type=EventType.CONVERSATION_STARTED,
        timestamp=200.0,
        payload={"agent_id": "agent_1", "topic": "plans"}
    )
    
    async_task = AsyncMock()
    
    # Process event
    manager.handle_event(event, task_fn=async_task)
    
    # Assertions
    assert handler_called == False
    queue_mock.enqueue.assert_called_once_with(
        task_fn=async_task,
        reasoning_type="conversation_started",
        agent_id="agent_1",
        current_state={"agent_id": "agent_1", "topic": "plans"},
        priority=1  # CONVERSATION_STARTED has priority 1
    )


def test_event_manager_priority_mapping() -> None:
    manager = EventManager()
    assert manager._get_priority(EventType.WITNESS_FOUND) == 0
    assert manager._get_priority(EventType.CONVERSATION_STARTED) == 1
    assert manager._get_priority(EventType.THEFT_OPPORTUNITY) == 1
    assert manager._get_priority(EventType.RUMOR_SPREAD) == 2
