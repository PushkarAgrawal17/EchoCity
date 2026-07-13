"""Unit tests for the AIRouter subsystem."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.llm.ai_router import AIRouter
from app.llm.queue import ReasoningQueue


def test_ai_router_factual_interrogation_bypasses_cognition() -> None:
    queue_mock = MagicMock(spec=ReasoningQueue)
    router = AIRouter(queue_mock)
    
    # Factual check payload
    payload = {"question": "what is your job?", "agent_id": "agent_1"}
    assert router.requires_cognition("interrogation", payload) == False


def test_ai_router_complex_interrogation_requires_cognition() -> None:
    queue_mock = MagicMock(spec=ReasoningQueue)
    router = AIRouter(queue_mock)
    
    # Complex query payload
    payload = {
        "question": "Can you explain why you were near the bank when the vault was open?",
        "agent_id": "agent_1"
    }
    assert router.requires_cognition("interrogation", payload) == True


def test_ai_router_routine_gossip_bypasses_cognition() -> None:
    queue_mock = MagicMock(spec=ReasoningQueue)
    router = AIRouter(queue_mock)
    
    payload = {"is_simple_routine": True}
    assert router.requires_cognition("gossip", payload) == False


def test_ai_router_routes_cognitive_to_queue() -> None:
    queue_mock = MagicMock(spec=ReasoningQueue)
    queue_mock.enqueue.return_value = "req_999"
    
    router = AIRouter(queue_mock)
    
    task_mock = AsyncMock()
    det_mock = MagicMock()
    
    payload = {"agent_id": "agent_1", "details": "nudged"}
    
    req_id = router.route(
        request_type="higher_self_reasoning",
        payload=payload,
        task_fn=task_mock,
        deterministic_service_fn=det_mock,
        priority=0
    )
    
    assert req_id == "req_999"
    queue_mock.enqueue.assert_called_once_with(
        task_fn=task_mock,
        reasoning_type="higher_self_reasoning",
        agent_id="agent_1",
        current_state=payload,
        priority=0
    )
    det_mock.assert_not_called()


def test_ai_router_routes_deterministic_directly() -> None:
    queue_mock = MagicMock(spec=ReasoningQueue)
    router = AIRouter(queue_mock)
    
    task_mock = AsyncMock()
    det_mock = MagicMock()
    
    payload = {"question": "hello", "agent_id": "agent_1"}
    
    req_id = router.route(
        request_type="interrogation",
        payload=payload,
        task_fn=task_mock,
        deterministic_service_fn=det_mock
    )
    
    assert req_id is None
    queue_mock.enqueue.assert_not_called()
    det_mock.assert_called_once()
