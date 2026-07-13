"""WebSocket endpoint for real-time simulation event streaming."""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["websocket"])


class ConnectionManager:
    """Manages active WebSocket connections and handles broadcasting messages."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New WebSocket connection accepted. Total active: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket disconnected. Total active: %d", len(self.active_connections))

    async def broadcast(self, message: dict) -> None:
        """Send a JSON payload to all connected clients."""
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("Failed to send message over WebSocket: %s", e)
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """FastAPI WebSocket route endpoint."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open by listening for client messages (heartbeats/commands)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket endpoint error: %s", e)
        manager.disconnect(websocket)
