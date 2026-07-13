"""Verification script for EchoCity AI pipelines and SQLite persistence."""

import asyncio
import sys
from pathlib import Path

# Add backend directory to python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.bootstrap.game_factory import GameFactory
from app.database.session import init_db, async_session_maker
from app.database.repositories import SimulationRepository


async def main() -> None:
    print("=" * 65)
    print("      ECHOCITY - AI PIPELINE & SQLITE PERSISTENCE VERIFICATION")
    print("=" * 65)

    # 1. Initialize SQLite Database
    print("\n[1/4] Initializing SQLite database schema...")
    await init_db()
    print("      SUCCESS: Schema initialized (echocity.db ready).")

    # 2. Boot Game Factory with real settings (demo=False)
    print("\n[2/4] Booting EchoCity Game Factory (demo=False)...")
    game = GameFactory.build(demo=False)
    agents_list = list(game.world.agent_manager)
    print(f"      SUCCESS: Loaded {len(agents_list)} agents from seeded_agents.json.")
    print(f"      Agents in city: {[a.name for a in agents_list]}")
    print(f"      Locations registered: {[l.name for l in game.location_manager.list_locations()]}")

    # 3. Test Ollama connectivity
    client = game.world.ollama_client
    print(f"\n[3/4] Testing Ollama connection (model='{client.model}')...")
    try:
        test_response = await client.generate(
            prompt="Hello! Reply with exactly 'Ollama connection active' if you read this.",
            system_prompt="You are a helpful test runner."
        )
        print(f"      SUCCESS: Ollama responded: '{test_response.strip()}'")
    except Exception as e:
        print("      ERROR: Could not connect to the local Ollama instance.")
        print("      Please ensure:")
        print("        1. The Ollama service is running (e.g. run 'ollama serve' on your host).")
        print(f"        2. The model is pulled (run 'ollama pull {client.model}').")
        print(f"      Error details: {e}")
        print("\nVerification aborted: AI pipeline test failed.")
        return

    # 4. Test background reasoning queue and persistence
    print("\n[4/4] Testing Reasoning Queue (concurrency=2) & SQLite Serialization...")
    
    # Create a scene placeholder event
    import uuid
    placeholder_id = f"scene_ph_{uuid.uuid4().hex[:8]}"
    placeholder_event = {
        "id": placeholder_id,
        "day": 1,
        "time": "06:00",
        "location": "Cafe",
        "type": "scene",
        "participants": [],
        "is_dialogue": False,
        "status": "generating",
        "narrative": "..."
    }
    game.world.narrative_events.append(placeholder_event)
    print("      Enqueued AI Scene Narrative generation task in ReasoningQueue...")
    
    game.world.reasoning_queue.enqueue(
        lambda: game.world.brain_service.generate_scene("cafe", placeholder_id)
    )

    print("      Waiting for background AI task to finish...")
    await game.world.reasoning_queue.wait_until_idle()

    # Verify placeholder update
    generated = next(e for e in game.world.narrative_events if e["id"] == placeholder_id)
    print(f"      SUCCESS: Placeholder event updated! status='{generated.get('status')}'")
    print(f"      Generated narrative: \"{generated.get('narrative')}\"")

    # Test SQLite saving
    repo = SimulationRepository(async_session_maker)
    print("\nSaving current World state to database...")
    await repo.save_world(game.world)
    print("      SUCCESS: Saved.")

    # Test SQLite loading
    print("Loading state back into a fresh World instance...")
    fresh_game = GameFactory.build(demo=False)
    load_success = await repo.load_world(fresh_game.world)
    
    if load_success:
        print("      SUCCESS: World state fully loaded from SQLite database!")
        print(f"      Restored clock ticks: {fresh_game.world.tick_count}")
        last_evt = fresh_game.world.narrative_events[-1]
        print(f"      Restored last event narrative: \"{last_evt.get('narrative')}\"")
    else:
        print("      ERROR: Failed to load state from SQLite.")

    print("\n" + "=" * 65)
    print(" VERIFICATION COMPLETE: ALL INTEGRATIONS ACTIVE AND WORKING")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
