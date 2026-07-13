from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.bootstrap.game_factory import Game
from app.core.dependencies import get_game

router = APIRouter(prefix="/api", tags=["command"])


class CommandRequest(BaseModel):
    command: str


class CommandResponse(BaseModel):
    output: str
    path: list[str]
    error: bool


@router.post("/command", response_model=CommandResponse)
def execute_command(
    payload: CommandRequest, 
    game: Annotated[Game, Depends(get_game)]
) -> CommandResponse:
    """Parse and execute a shell command inside the active simulation game."""
    try:
        output = game.shell.execute_line(payload.command)
        current_path = list(game.shell._path)
        
        # Check if the output string suggests an execution error
        is_error = (
            "Usage:" in output or 
            "not found" in output or 
            "Invalid" in output or 
            "No such" in output or
            "not in a location" in output
        )
        
        return CommandResponse(
            output=output,
            path=current_path,
            error=is_error
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
