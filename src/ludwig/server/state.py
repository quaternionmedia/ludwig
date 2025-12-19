"""State Manager

Central state management for the mixer application.
Maintains synchronized state between hardware, API, and connected clients.
"""

from typing import Optional, Any
import asyncio
from ludwig.models import (
    MixerState,
    Channel,
    ParameterChange,
    DeviceInfo,
    Scene,
)


class StateManager:
    """
    Central state manager for Ludwig.

    Responsibilities:
    - Maintain current mixer state
    - Synchronize with hardware via plugins
    - Apply and validate parameter changes
    - Manage scenes and snapshots
    """

    def __init__(self):
        self._state: Optional[MixerState] = None
        self._plugins: dict[str, Any] = {}  # device_id -> plugin instance
        self._scenes: list[Scene] = []
        self._meters: dict[str, float] = {}
        self._lock = asyncio.Lock()

    # =========================================================================
    # Device Management
    # =========================================================================

    async def connect_device(self, device_type: str, connection_string: str) -> bool:
        """
        Connect to a mixer device.

        Args:
            device_type: Plugin type identifier
            connection_string: Connection details

        Returns:
            True if connection successful
        """
        async with self._lock:
            # TODO: Load plugin based on device_type
            # plugin = load_plugin(device_type)
            # success = plugin.connect()
            # if success:
            #     self._plugins[plugin.get_device_info().id] = plugin
            #     self._state = plugin.sync_state()
            # return success

            # Placeholder implementation
            return True

    async def disconnect_device(self, device_id: str) -> None:
        """Disconnect from a specific device."""
        async with self._lock:
            if device_id in self._plugins:
                self._plugins[device_id].disconnect()
                del self._plugins[device_id]

    async def disconnect_all(self) -> None:
        """Disconnect from all devices."""
        async with self._lock:
            for plugin in self._plugins.values():
                plugin.disconnect()
            self._plugins.clear()
            self._state = None

    def get_connected_devices(self) -> list[DeviceInfo]:
        """Get list of connected devices."""
        return [p.get_device_info() for p in self._plugins.values()]

    # =========================================================================
    # State Access
    # =========================================================================

    def get_state(self) -> Optional[MixerState]:
        """Get current mixer state."""
        return self._state

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a specific channel's state."""
        if self._state and channel_id in self._state.channels:
            return self._state.channels[channel_id]
        return None

    def get_meters(self) -> dict[str, float]:
        """Get current meter values."""
        return self._meters.copy()

    # =========================================================================
    # Parameter Control
    # =========================================================================

    async def set_fader(self, channel_id: str, level: float) -> None:
        """Set channel fader level."""
        if not self._state or channel_id not in self._state.channels:
            return

        # Clamp value
        level = max(0.0, min(1.0, level))

        # Update local state
        self._state.channels[channel_id].fader = level

        # Send to hardware
        for plugin in self._plugins.values():
            plugin.set_fader(channel_id, level)

    async def set_mute(self, channel_id: str, muted: bool) -> None:
        """Set channel mute state."""
        if not self._state or channel_id not in self._state.channels:
            return

        self._state.channels[channel_id].mute = muted

        for plugin in self._plugins.values():
            plugin.set_mute(channel_id, muted)

    async def set_pan(self, channel_id: str, pan: float) -> None:
        """Set channel pan position."""
        if not self._state or channel_id not in self._state.channels:
            return

        # Clamp value
        pan = max(-1.0, min(1.0, pan))

        self._state.channels[channel_id].pan = pan

        for plugin in self._plugins.values():
            plugin.set_pan(channel_id, pan)

    async def apply_parameter_change(self, change: ParameterChange) -> None:
        """Apply a generic parameter change."""
        if not self._state:
            return

        channel_id = change.channel_id
        parameter = change.parameter
        value = change.value

        if channel_id not in self._state.channels:
            return

        channel = self._state.channels[channel_id]

        # Handle common parameters
        if parameter == "fader":
            await self.set_fader(channel_id, float(value))
        elif parameter == "mute":
            await self.set_mute(channel_id, bool(value))
        elif parameter == "pan":
            await self.set_pan(channel_id, float(value))
        elif parameter == "solo":
            channel.solo = bool(value)
        elif parameter.startswith("eq."):
            # Handle nested EQ parameters
            self._apply_nested_parameter(channel.eq, parameter[3:], value)
        elif parameter.startswith("compressor."):
            self._apply_nested_parameter(channel.compressor, parameter[11:], value)
        elif parameter.startswith("gate."):
            self._apply_nested_parameter(channel.gate, parameter[5:], value)

    def _apply_nested_parameter(self, obj: Any, path: str, value: Any) -> None:
        """Apply a value to a nested object path like 'bands.0.gain'."""
        parts = path.split(".")

        for part in parts[:-1]:
            if part.isdigit():
                obj = obj[int(part)]
            else:
                obj = getattr(obj, part)

        final_key = parts[-1]
        if final_key.isdigit():
            obj[int(final_key)] = value
        else:
            setattr(obj, final_key, value)

    # =========================================================================
    # Scene Management
    # =========================================================================

    def get_scenes(self) -> list[Scene]:
        """Get list of available scenes."""
        return self._scenes

    async def recall_scene(self, scene_number: int) -> None:
        """Recall a scene by number."""
        for plugin in self._plugins.values():
            plugin.recall_scene(scene_number)

        # Sync state after scene recall
        await asyncio.sleep(0.1)  # Give hardware time to respond
        for plugin in self._plugins.values():
            self._state = plugin.sync_state()

    # =========================================================================
    # Hardware Callbacks
    # =========================================================================

    def on_hardware_parameter_change(self, change: ParameterChange) -> None:
        """Handle parameter change from hardware."""
        if self._state and change.channel_id in self._state.channels:
            # Update local state
            # This will be called by plugins when hardware changes
            pass

    def on_hardware_meter_update(self, meters: dict[str, float]) -> None:
        """Handle meter update from hardware."""
        self._meters.update(meters)
