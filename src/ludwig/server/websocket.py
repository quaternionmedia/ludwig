"""WebSocket Connection Manager

Handles WebSocket connections and broadcasts for real-time updates.
"""

from typing import Optional, Any
from fastapi import WebSocket
import json


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts.

    Features:
    - Track active connections
    - Broadcast to all or filtered clients
    - Handle subscriptions for selective updates
    """

    def __init__(self):
        self._connections: list[WebSocket] = []
        self._subscriptions: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and track a new WebSocket connection."""
        await websocket.accept()
        self._connections.append(websocket)
        self._subscriptions[websocket] = set()

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if websocket in self._connections:
            self._connections.remove(websocket)
        if websocket in self._subscriptions:
            del self._subscriptions[websocket]

    def set_subscriptions(self, websocket: WebSocket, channels: list[str]) -> None:
        """Set channel subscriptions for a client."""
        self._subscriptions[websocket] = set(channels)

    async def broadcast(
        self,
        message: dict,
        exclude: Optional[WebSocket] = None,
    ) -> None:
        """Broadcast a message to all connected clients."""
        disconnected = []

        for connection in self._connections:
            if connection == exclude:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_parameter_change(
        self,
        channel_id: str,
        parameter: str,
        value: Any,
        exclude: Optional[WebSocket] = None,
    ) -> None:
        """Broadcast a parameter change to relevant clients."""
        message = {
            "type": "parameter",
            "channel_id": channel_id,
            "parameter": parameter,
            "value": value,
        }

        disconnected = []

        for connection in self._connections:
            if connection == exclude:
                continue

            # Check subscription filter
            subs = self._subscriptions.get(connection, set())
            if subs and channel_id not in subs:
                continue

            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_batch_changes(
        self,
        changes: list,
        exclude: Optional[WebSocket] = None,
    ) -> None:
        """Broadcast multiple parameter changes."""
        message = {
            "type": "batch",
            "changes": [
                {
                    "channel_id": c.channel_id,
                    "parameter": c.parameter,
                    "value": c.value,
                }
                for c in changes
            ],
        }
        await self.broadcast(message, exclude=exclude)

    async def broadcast_meters(self, meters: dict[str, float]) -> None:
        """Broadcast meter updates to all clients."""
        message = {
            "type": "meters",
            "levels": meters,
        }

        disconnected = []

        for connection in self._connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_state_update(self, state) -> None:
        """Broadcast full state update (e.g., after scene recall)."""
        if state is None:
            return

        message = {
            "type": "state",
            "data": state.model_dump(),
        }
        await self.broadcast(message)

    @property
    def connection_count(self) -> int:
        """Get number of active connections."""
        return len(self._connections)
