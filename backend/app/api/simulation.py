from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.bootstrap.game_factory import Game
from app.core.dependencies import get_game

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


class SimulationStatusResponse(BaseModel):
    is_running: bool
    active_scene: str
    scene_step: int
    tick_count: int


class GeneralResponse(BaseModel):
    success: bool
    message: str


class SceneRequest(BaseModel):
    scene: str


@router.get("/status", response_model=SimulationStatusResponse)
def get_simulation_status(game: Annotated[Game, Depends(get_game)]) -> SimulationStatusResponse:
    """Retrieve the current state of the simulation tick loop."""
    return SimulationStatusResponse(
        is_running=game.world.is_running,
        active_scene=game.world.active_scene,
        scene_step=game.world.scene_step,
        tick_count=game.world.tick_count
    )


@router.post("/start", response_model=GeneralResponse)
def start_simulation(game: Annotated[Game, Depends(get_game)]) -> GeneralResponse:
    """Activate the background simulation tick loop."""
    if game.world.is_running:
        return GeneralResponse(success=True, message="Simulation already running.")
    game.world.start()
    return GeneralResponse(success=True, message="Simulation started successfully.")


@router.post("/stop", response_model=GeneralResponse)
def stop_simulation(game: Annotated[Game, Depends(get_game)]) -> GeneralResponse:
    """Pause the background simulation tick loop."""
    if not game.world.is_running:
        return GeneralResponse(success=True, message="Simulation already paused.")
    game.world.stop()
    return GeneralResponse(success=True, message="Simulation paused successfully.")


from fastapi import Request

@router.post("/save", response_model=GeneralResponse)
async def save_simulation(
    request: Request,
    game: Annotated[Game, Depends(get_game)]
) -> GeneralResponse:
    """Commit active records to SQLite database."""
    if hasattr(request.app.state, "db_repo"):
        await request.app.state.db_repo.save_world(game.world)
        return GeneralResponse(
            success=True,
            message=f"Simulation state committed to SQLite. Saved tick frame {game.world.tick_count}."
        )
    return GeneralResponse(success=False, message="Database repository not initialized.")


@router.get("/events")
def get_simulation_events(game: Annotated[Game, Depends(get_game)]):
    """Retrieve all generated narrative events in reverse chronological order."""
    # Reverse events to display the newest events at the top of the feed
    return list(reversed(game.world.narrative_events))


@router.post("/reset", response_model=GeneralResponse)
async def reset_simulation(
    request: Request,
    game: Annotated[Game, Depends(get_game)]
) -> GeneralResponse:
    """Reset the scene steps, clock ticks, and narrative logs."""
    game.world.stop()
    game.world.tick_count = 0
    game.world.scene_step = 0
    game.world.active_scene = "cafe"
    game.world.narrative_events = []
    if hasattr(game.world, "case_file"):
        game.world.case_file.clear()
    
    # Re-bootstrap the agents if not in demo mode
    if not game.world.demo:
        from app.bootstrap.game_factory import GameFactory
        fresh_game = GameFactory.build(demo=False)
        game.world.agent_manager = fresh_game.world.agent_manager
        game.world.memory_manager = fresh_game.world.memory_manager
        game.world.diaries = fresh_game.world.diaries
        game.world.clock = fresh_game.world.clock
    
    game.world.start()

    if hasattr(request.app.state, "db_repo"):
        await request.app.state.db_repo.save_world(game.world)

    return GeneralResponse(success=True, message="Simulation reset to beginning Cafe gossip scene.")


@router.post("/scene", response_model=GeneralResponse)
def change_simulation_scene(payload: SceneRequest, game: Annotated[Game, Depends(get_game)]) -> GeneralResponse:
    """Change the active scene context (cafe or court) and reset step logs."""
    scene = payload.scene.lower()
    if scene not in ["cafe", "court"]:
        return GeneralResponse(success=False, message="Invalid scene context. Choose 'cafe' or 'court'.")

    # Change world state variables
    game.world.active_scene = scene
    game.world.scene_step = 0
    
    # Move the shell path as well to keep contexts aligned
    game.shell._path = ["locations", scene]

    # Pre-populate first 3 narrative scripts of the new scene immediately
    if game.world.demo:
        for _ in range(3):
            game.world._process_scene_tick()
    else:
        import uuid
        day = int(game.world.clock.current_time // 86400) + 1
        hours = int((game.world.clock.current_time % 86400) // 3600)
        minutes = int((game.world.clock.current_time % 3600) // 60)
        time_str = f"{hours:02d}:{minutes:02d}"

        location = game.world.location_manager.get(scene)
        location_name = location.name if location else scene.capitalize()

        placeholder_id = f"scene_ph_{uuid.uuid4().hex[:8]}"
        placeholder_event = {
            "id": placeholder_id,
            "day": day,
            "time": time_str,
            "location": location_name,
            "type": "scene",
            "participants": [],
            "is_dialogue": False,
            "status": "generating",
            "narrative": "..."
        }
        game.world.narrative_events.append(placeholder_event)

        game.world.reasoning_queue.enqueue(
            lambda p_id=placeholder_id: game.world.brain_service.generate_scene(scene, p_id)
        )

    return GeneralResponse(
        success=True,
        message=f"Simulation scene changed to {scene.upper()}."
    )


@router.get("/agents")
def get_simulation_agents(game: Annotated[Game, Depends(get_game)]):
    """Retrieve details of all active agents in the simulation world."""
    agents_list = []
    for agent in game.world.agent_manager:
        memories = game.world.memory_manager.get_memories(agent.agent_id)
        memory_count = len(memories) if memories else 0
        
        relationships = []
        for target_id, rel in agent.relationships.items():
            if rel.friendship >= 0.7:
                label = "Friend"
            elif rel.trust >= 0.7:
                label = "Trusts"
            elif rel.respect >= 0.7:
                label = "Respects"
            elif rel.fear >= 0.5:
                label = "Fears"
            elif rel.trust <= 0.35:
                label = "Wary of"
            else:
                label = "Acquaintance"
            
            affinity = int((rel.friendship * 0.6 + rel.trust * 0.4) * 200 - 100)
            affinity = max(-100, min(100, affinity))
            
            relationships.append({
                "agentId": target_id,
                "label": label,
                "affinity": affinity
            })
            
        agents_list.append({
            "agent_id": agent.agent_id,
            "name": agent.name,
            "state": agent.state.name,
            "goal": agent.goal or "",
            "location_id": agent.location.id if agent.location else None,
            "age": agent.age,
            "occupation": agent.occupation,
            "home": agent.home,
            "personality": getattr(agent, "personality", {}),
            "stress": agent.stress,
            "suspicion": agent.suspicion,
            "energy": agent.energy,
            "confidence": agent.confidence,
            "emotion": agent.emotion,
            "inventory": agent.inventory,
            "memory_count": memory_count,
            "relationships": relationships
        })
    return agents_list


@router.get("/check-connections")
async def check_connections(
    request: Request,
    game: Annotated[Game, Depends(get_game)]
):
    """Check database and Ollama (model) connection status."""
    db_status = "failed"
    ollama_status = "failed"
    ollama_error = None
    db_error = None
    
    # 1. Check SQLite DB
    try:
        if hasattr(request.app.state, "db_repo") and request.app.state.db_repo:
            async with request.app.state.db_repo.session_maker() as session:
                from sqlalchemy import text
                await session.execute(text("SELECT 1"))
                db_status = "success"
        else:
            db_error = "Repository not initialized"
    except Exception as e:
        db_error = str(e)
        
    # 2. Check Ollama
    try:
        from app.core.config import get_settings
        settings = get_settings()
        import httpx
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            if response.status_code == 200:
                ollama_status = "success"
                models_data = response.json().get("models", [])
                model_names = [m.get("name") for m in models_data]
                target = settings.ollama_model
                has_model = any(target in name or name in target for name in model_names)
                if not has_model:
                    ollama_status = "model_not_found"
            else:
                ollama_error = f"Ollama returned status {response.status_code}"
    except Exception as e:
        ollama_error = str(e)
        
    return {
        "db": db_status,
        "db_error": db_error,
        "ollama": ollama_status,
        "ollama_error": ollama_error,
        "ollama_model": get_settings().ollama_model
    }

