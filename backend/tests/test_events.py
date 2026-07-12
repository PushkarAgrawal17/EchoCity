"""Unit tests for the events subsystem."""

from app.events.event import Event
from app.events.event_bus import EventBus
from app.events.event_type import EventType


def test_event_auto_generates_unique_ids() -> None:
    e1 = Event(event_type=EventType.TICK, timestamp=0.0)
    e2 = Event(event_type=EventType.TICK, timestamp=0.0)
    assert e1.event_id != e2.event_id


def test_event_defaults_to_empty_payload() -> None:
    event = Event(event_type=EventType.TICK, timestamp=0.0)
    assert event.payload == {}


def test_event_carries_given_payload() -> None:
    event = Event(event_type=EventType.AGENT_REGISTERED, timestamp=5.0, payload={"agent_id": "a1"})
    assert event.payload == {"agent_id": "a1"}


def test_subscriber_receives_published_event() -> None:
    bus = EventBus()
    received = []
    bus.subscribe(EventType.TICK, received.append)

    event = Event(event_type=EventType.TICK, timestamp=1.0)
    bus.publish(event)

    assert received == [event]


def test_subscriber_only_receives_its_event_type() -> None:
    bus = EventBus()
    received = []
    bus.subscribe(EventType.WORLD_STARTED, received.append)

    bus.publish(Event(event_type=EventType.TICK, timestamp=1.0))

    assert received == []


def test_multiple_subscribers_all_called_in_order() -> None:
    bus = EventBus()
    order = []
    bus.subscribe(EventType.TICK, lambda e: order.append("first"))
    bus.subscribe(EventType.TICK, lambda e: order.append("second"))

    bus.publish(Event(event_type=EventType.TICK, timestamp=1.0))

    assert order == ["first", "second"]


def test_publish_with_no_subscribers_does_not_raise() -> None:
    bus = EventBus()
    bus.publish(Event(event_type=EventType.TICK, timestamp=1.0))  # should not raise


def test_unsubscribe_stops_future_notifications() -> None:
    bus = EventBus()
    received = []

    def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(EventType.TICK, handler)
    bus.unsubscribe(EventType.TICK, handler)
    bus.publish(Event(event_type=EventType.TICK, timestamp=1.0))

    assert received == []


def test_unsubscribe_unknown_subscriber_is_noop() -> None:
    bus = EventBus()

    def handler(event: Event) -> None:
        pass

    bus.unsubscribe(EventType.TICK, handler)  # should not raise
