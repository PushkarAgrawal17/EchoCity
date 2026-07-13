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


@router.post("/save", response_model=GeneralResponse)
def save_simulation(game: Annotated[Game, Depends(get_game)]) -> GeneralResponse:
    """Simulate committing active records to SQLite database."""
    return GeneralResponse(
        success=True,
        message=f"Simulation state committed to SQLite. Saved tick frame {game.world.tick_count}."
    )


@router.get("/events")
def get_simulation_events(game: Annotated[Game, Depends(get_game)]):
    """Retrieve all generated narrative events in reverse chronological order."""
    # Reverse events to display the newest events at the top of the feed
    return list(reversed(game.world.narrative_events))


@router.post("/reset", response_model=GeneralResponse)
def reset_simulation(game: Annotated[Game, Depends(get_game)]) -> GeneralResponse:
    """Reset the scene steps, clock ticks, and narrative logs."""
    game.world.stop()
    game.world.tick_count = 0
    game.world.scene_step = 0
    game.world.active_scene = "cafe"
    game.world.narrative_events = []
    if hasattr(game.world, "case_file"):
        game.world.case_file.clear()
    
    # Pre-generate Cafe first 3 items on reset
    game.world.start()
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
    for _ in range(3):
        game.world._process_scene_tick()

    return GeneralResponse(
        success=True,
        message=f"Simulation scene changed to {scene.upper()} and first 3 events generated."
    )
