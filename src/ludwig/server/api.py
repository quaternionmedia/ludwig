"""Ludwig API Server

FastAPI server exposing mixer control via REST and WebSocket endpoints.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import asyncio
import json

from ludwig.models import (
    MixerState,
    Channel,
    ParameterChange,
    BatchParameterChange,
    MeterUpdate,
    DeviceInfo,
    Scene,
)
from ludwig.server.state import StateManager
from ludwig.server.websocket import ConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    app.state.state_manager = StateManager()
    app.state.ws_manager = ConnectionManager()

    # Start meter broadcast task
    app.state.meter_task = asyncio.create_task(
        meter_broadcast_loop(app.state.state_manager, app.state.ws_manager)
    )

    yield

    # Shutdown
    app.state.meter_task.cancel()
    await app.state.state_manager.disconnect_all()


app = FastAPI(
    title="Ludwig Mixer API",
    description="Remote control API for audio mixing consoles",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Dependencies
# =============================================================================


def get_state_manager() -> StateManager:
    """Dependency to get the state manager."""
    return app.state.state_manager


def get_ws_manager() -> ConnectionManager:
    """Dependency to get the WebSocket manager."""
    return app.state.ws_manager


# =============================================================================
# REST Endpoints - Device Management
# =============================================================================


@app.get("/api/devices", response_model=list[DeviceInfo])
async def list_devices(state: StateManager = Depends(get_state_manager)):
    """List all available/connected mixer devices."""
    return state.get_connected_devices()


@app.post("/api/devices/connect")
async def connect_device(
    device_type: str,
    connection_string: str,
    state: StateManager = Depends(get_state_manager),
):
    """
    Connect to a mixer device.

    Args:
        device_type: Plugin identifier (e.g., "qu24", "xair", "x32")
        connection_string: Connection details (e.g., MIDI port or IP:port)
    """
    success = await state.connect_device(device_type, connection_string)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to connect to device")
    return {"status": "connected", "device_type": device_type}


@app.post("/api/devices/{device_id}/disconnect")
async def disconnect_device(
    device_id: str,
    state: StateManager = Depends(get_state_manager),
):
    """Disconnect from a mixer device."""
    await state.disconnect_device(device_id)
    return {"status": "disconnected"}


# =============================================================================
# REST Endpoints - Mixer State
# =============================================================================


@app.get("/api/mixer/state", response_model=MixerState)
async def get_mixer_state(state: StateManager = Depends(get_state_manager)):
    """Get complete current mixer state."""
    mixer_state = state.get_state()
    if not mixer_state:
        raise HTTPException(status_code=404, detail="No mixer connected")
    return mixer_state


@app.get("/api/mixer/channels", response_model=list[Channel])
async def get_channels(state: StateManager = Depends(get_state_manager)):
    """Get all channel states."""
    mixer_state = state.get_state()
    if not mixer_state:
        raise HTTPException(status_code=404, detail="No mixer connected")
    return list(mixer_state.channels.values())


@app.get("/api/mixer/channels/{channel_id}", response_model=Channel)
async def get_channel(
    channel_id: str,
    state: StateManager = Depends(get_state_manager),
):
    """Get a specific channel's state."""
    mixer_state = state.get_state()
    if not mixer_state:
        raise HTTPException(status_code=404, detail="No mixer connected")
    if channel_id not in mixer_state.channels:
        raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
    return mixer_state.channels[channel_id]


# =============================================================================
# REST Endpoints - Parameter Control
# =============================================================================


@app.post("/api/mixer/channels/{channel_id}/fader")
async def set_fader(
    channel_id: str,
    level: float,
    state: StateManager = Depends(get_state_manager),
    ws: ConnectionManager = Depends(get_ws_manager),
):
    """Set channel fader level (0.0-1.0)."""
    await state.set_fader(channel_id, level)
    await ws.broadcast_parameter_change(channel_id, "fader", level)
    return {"channel_id": channel_id, "fader": level}


@app.post("/api/mixer/channels/{channel_id}/mute")
async def set_mute(
    channel_id: str,
    muted: bool,
    state: StateManager = Depends(get_state_manager),
    ws: ConnectionManager = Depends(get_ws_manager),
):
    """Set channel mute state."""
    await state.set_mute(channel_id, muted)
    await ws.broadcast_parameter_change(channel_id, "mute", muted)
    return {"channel_id": channel_id, "mute": muted}


@app.post("/api/mixer/channels/{channel_id}/pan")
async def set_pan(
    channel_id: str,
    pan: float,
    state: StateManager = Depends(get_state_manager),
    ws: ConnectionManager = Depends(get_ws_manager),
):
    """Set channel pan (-1.0 to 1.0)."""
    await state.set_pan(channel_id, pan)
    await ws.broadcast_parameter_change(channel_id, "pan", pan)
    return {"channel_id": channel_id, "pan": pan}


@app.post("/api/mixer/parameters")
async def set_parameters(
    batch: BatchParameterChange,
    state: StateManager = Depends(get_state_manager),
    ws: ConnectionManager = Depends(get_ws_manager),
):
    """Apply multiple parameter changes at once."""
    for change in batch.changes:
        await state.apply_parameter_change(change)
    await ws.broadcast_batch_changes(batch.changes)
    return {"applied": len(batch.changes)}


# =============================================================================
# REST Endpoints - Scenes
# =============================================================================


@app.get("/api/scenes", response_model=list[Scene])
async def list_scenes(state: StateManager = Depends(get_state_manager)):
    """List all available scenes."""
    return state.get_scenes()


@app.post("/api/scenes/{scene_number}/recall")
async def recall_scene(
    scene_number: int,
    state: StateManager = Depends(get_state_manager),
    ws: ConnectionManager = Depends(get_ws_manager),
):
    """Recall a scene by number."""
    await state.recall_scene(scene_number)
    # After scene recall, broadcast full state update
    await ws.broadcast_state_update(state.get_state())
    return {"recalled": scene_number}


# =============================================================================
# WebSocket Endpoint
# =============================================================================


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    ws: ConnectionManager = Depends(get_ws_manager),
    state: StateManager = Depends(get_state_manager),
):
    """
    WebSocket endpoint for real-time bidirectional communication.

    Message format (JSON):
        {
            "type": "fader" | "mute" | "pan" | "parameter" | "subscribe" | "ping",
            "channel_id": "input_1",
            "value": 0.75,
            "parameter": "eq.bands.0.gain"  // for type="parameter"
        }

    Server sends:
        - Parameter changes (same format)
        - Meter updates: {"type": "meters", "levels": {"input_1": 0.5, ...}}
        - State sync: {"type": "state", "data": {...full mixer state...}}
    """
    await ws.connect(websocket)

    try:
        # Send initial state on connect
        initial_state = state.get_state()
        if initial_state:
            await websocket.send_json(
                {
                    "type": "state",
                    "data": initial_state.model_dump(),
                }
            )

        while True:
            data = await websocket.receive_json()
            await handle_websocket_message(data, websocket, state, ws)

    except WebSocketDisconnect:
        ws.disconnect(websocket)


async def handle_websocket_message(
    data: dict,
    websocket: WebSocket,
    state: StateManager,
    ws: ConnectionManager,
):
    """Handle incoming WebSocket message."""
    msg_type = data.get("type")
    channel_id = data.get("channel_id")
    value = data.get("value")

    if msg_type == "fader" and channel_id is not None and value is not None:
        await state.set_fader(channel_id, value)
        await ws.broadcast_parameter_change(
            channel_id, "fader", value, exclude=websocket
        )

    elif msg_type == "mute" and channel_id is not None and value is not None:
        await state.set_mute(channel_id, value)
        await ws.broadcast_parameter_change(
            channel_id, "mute", value, exclude=websocket
        )

    elif msg_type == "pan" and channel_id is not None and value is not None:
        await state.set_pan(channel_id, value)
        await ws.broadcast_parameter_change(channel_id, "pan", value, exclude=websocket)

    elif msg_type == "parameter":
        parameter = data.get("parameter")
        if channel_id and parameter and value is not None:
            change = ParameterChange(
                channel_id=channel_id,
                parameter=parameter,
                value=value,
                source="websocket",
            )
            await state.apply_parameter_change(change)
            await ws.broadcast_parameter_change(
                channel_id, parameter, value, exclude=websocket
            )

    elif msg_type == "ping":
        await websocket.send_json({"type": "pong"})

    elif msg_type == "subscribe":
        # Subscribe to specific channels or meter updates
        subscriptions = data.get("channels", [])
        ws.set_subscriptions(websocket, subscriptions)


async def meter_broadcast_loop(
    state: StateManager,
    ws: ConnectionManager,
    interval: float = 0.05,  # 50ms = 20 Hz
):
    """Background task to broadcast meter updates."""
    while True:
        try:
            meters = state.get_meters()
            if meters:
                await ws.broadcast_meters(meters)
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Meter broadcast error: {e}")
            await asyncio.sleep(1)  # Back off on error


# =============================================================================
# Entry Point
# =============================================================================


def main():
    """Run the API server."""
    import uvicorn

    uvicorn.run(
        "ludwig.server.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
