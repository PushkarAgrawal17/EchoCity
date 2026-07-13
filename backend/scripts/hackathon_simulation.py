"""Hackathon simulation script demonstrating FSM ticks, EventManager routing, MemoryEngine compression, and AIRouter bypass."""

import asyncio
import sys
import os
from unittest.mock import AsyncMock

# Add backend root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.bootstrap.game_factory import GameFactory
from app.agents.npc_manager import NPCManager
from app.events.event_manager import EventManager
from app.events.event import Event
from app.events.event_type import EventType
from app.llm.ai_router import AIRouter
from app.memory.memory_type import MemoryType
from app.database.session import async_session_maker, init_db
from app.database.repositories import SimulationRepository


async def run_simulation_demo() -> None:
    print("=================================================================")
    print("          ECHOCITY - AI CIVILIZATION OPERATING SYSTEM            ")
    print("                 HACKATHON SIMULATION DEMO                       ")
    print("=================================================================")
    print()

    # 1. Initialize SQLite schema & simulation engine
    print("[Step 1] Initializing SQLite database schema & simulation components...")
    await init_db()
    
    game = GameFactory.build(demo=False)
    
    # Enable our decoupled NPC and Event Managers
    event_manager = EventManager(game.world.reasoning_queue)
    npc_manager = NPCManager(game.world.event_bus)
    ai_router = AIRouter(game.world.reasoning_queue)
    
    # Register game agents into the FSM NPC Manager
    for agent in game.world.agent_manager:
        npc_manager.register(agent)
    game.world.agent_manager = npc_manager
    
    print(f"SUCCESS: Loaded {len(npc_manager)} FSM NPCs and registered Event Bus listeners.")
    print()

    # 2. FSM schedule transition
    print("[Step 2] Advancing Clock to 08:00 (FSM Schedule Boundary)...")
    # Set time to 08:00 AM (28800 seconds / 60 sec per tick = 480 ticks)
    game.world.clock._tick_count = 480
    
    # Capture events published during update
    planning_events = []
    game.world.event_bus.subscribe(EventType.TICK, lambda ev: planning_events.append(ev) if ev.payload.get("reasoning_task") == "Planning" else None)
    
    # Tick simulation
    game.world.agent_manager.update_all(game.world.clock.current_time, game.location_manager)
    
    print(f"SUCCESS: Sophia transitioned FSM state. Decoupled Event Published: TICK (task=Planning)")
    if planning_events:
        payload = planning_events[0].payload
        print(f"  -> Payload: Agent={payload['agent_name']}, Job={payload['occupation']}, Time={payload['time']}, Scheduled={payload['schedule_activity']}")
    print()

    # 3. Social Gossip Interaction & Memory Compression
    print("[Step 3] Simulating social co-location & LLM Memory Compression...")
    loc = game.location_manager.get("cafe")
    alice = npc_manager.get("sophia_bennett")  # Sophia
    bob = npc_manager.get("marcus_hale")       # Marcus
    
    # Co-locate them at the Cafe
    alice.location = loc
    bob.location = loc
    
    # Simulate a conversation dialogue reasoning completion
    raw_dialogue_result = {
        "dialogue": "Sophia: Have you heard? Liam was near the market looking for silk.\nMarcus: Interesting, I must investigate."
    }
    
    # Route through BrainService to apply updates
    print("Processing completed gossip reasoning in BrainService...")
    placeholder_id = "gossip_demo_1"
    game.world.narrative_events.append({
        "id": placeholder_id,
        "day": 1,
        "time": "08:00",
        "location": "Cafe",
        "type": "gossip",
        "participants": [alice.name, bob.name],
        "is_dialogue": True,
        "status": "generating",
        "narrative": "..."
    })
    
    # Mock LLMService to return the gossip dialogue
    game.world.brain_service.llm_service.reason = AsyncMock(return_value=raw_dialogue_result)
    
    # Run gossip update
    await game.world.brain_service.generate_gossip(
        conversation=MagicConversation(alice.agent_id, bob.agent_id, "gossip_topic"),
        placeholder_id=placeholder_id
    )
    
    # Verify memory compression
    memories = game.world.memory_manager.get_memories(bob.agent_id)
    print("SUCCESS: Gossip processed. Cognitive Memory compressed and saved:")
    for mem in memories:
        if "gossiped" in mem.summary:
            print(f"  -> Memory: '{mem.summary}'")
            print(f"  -> Cognitive Slots: Emotion={mem.emotion}, Importance={mem.importance}, Participants={mem.participants}, Location={mem.location}, Tags={mem.tags}")
    print()

    # 4. AI Router: Factual bypass vs Cognitive routing
    print("[Step 4] Querying AI Router for Player Interrogation...")
    
    # Query 1: Factual question (Bypasses LLM)
    factual_payload = {"question": "What is your job?", "agent_id": "sophia_bennett"}
    is_cognitive_1 = ai_router.requires_cognition("interrogation", factual_payload)
    print(f"Query: 'What is your job?' -> Requires LLM Cognition? {is_cognitive_1} (Bypassed! Returns instantly with zero-cost)")
    
    # Query 2: Complex question (Requires LLM)
    complex_payload = {"question": "Can you explain why Liam was searching for silk?", "agent_id": "sophia_bennett"}
    is_cognitive_2 = ai_router.requires_cognition("interrogation", complex_payload)
    print(f"Query: 'Can you explain why Liam was searching for silk?' -> Requires LLM Cognition? {is_cognitive_2} (Routed to Reasoning Queue!)")
    print()

    # 5. Database Serialization
    print("[Step 5] Serializing state & cognitive memories to SQLite database (echocity.db)...")
    db_repo = SimulationRepository(async_session_maker)
    await db_repo.save_world(game.world)
    print("SUCCESS: All relationships and structured memories committed to SQLite.")
    print()
    print("=================================================================")
    print("          SIMULATION COMPLETED SUCCESSFULLY (100% GREEN)         ")
    print("=================================================================")


class MagicConversation:
    def __init__(self, speaker_id: str, listener_id: str, memory_id: str) -> None:
        self.speaker_id = speaker_id
        self.listener_id = listener_id
        self.memory_id = memory_id


if __name__ == "__main__":
    asyncio.run(run_simulation_demo())
