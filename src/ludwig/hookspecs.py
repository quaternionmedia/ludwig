"""Ludwig Plugin Specifications

Enhanced pluggy hookspecs for the mixer plugin system.
This module defines the contract that all board plugins must implement.
"""

from pluggy import HookspecMarker, HookimplMarker
from typing import Optional, Any
from ludwig.models import (
    Channel,
    MixerState,
    DeviceInfo,
    DeviceCapabilities,
    Scene,
    ParameterChange,
    NormalizedValue,
    PanValue,
    EQBand,
    Compressor,
    Gate,
)

# Hook markers
hookspec = HookspecMarker("ludwig")
hookimpl = HookimplMarker("ludwig")


class MixerSpec:
    """
    Mixer plugin specification.

    All board plugins must implement these hooks. The methods use normalized
    values (0.0-1.0) which plugins translate to protocol-specific values.
    """

    # =========================================================================
    # Connection Lifecycle
    # =========================================================================

    @hookspec
    def connect(self) -> bool:
        """
        Establish connection to the mixer hardware.

        Returns:
            True if connection successful, False otherwise
        """

    @hookspec
    def disconnect(self) -> None:
        """Close connection to the mixer hardware."""

    @hookspec
    def is_connected(self) -> bool:
        """Check if currently connected to hardware."""

    @hookspec
    def get_device_info(self) -> DeviceInfo:
        """
        Get information about the connected device.

        Returns:
            DeviceInfo with capabilities and connection details
        """

    # =========================================================================
    # State Synchronization
    # =========================================================================

    @hookspec
    def sync_state(self) -> MixerState:
        """
        Request full state sync from hardware.

        Queries the mixer for all current values and returns
        a complete MixerState object.

        Returns:
            Complete current mixer state
        """

    @hookspec
    def get_channel_state(self, channel_id: str) -> Optional[Channel]:
        """
        Get current state of a single channel.

        Args:
            channel_id: The channel identifier

        Returns:
            Channel state or None if channel doesn't exist
        """

    # =========================================================================
    # Fader Section
    # =========================================================================

    @hookspec
    def set_fader(self, channel_id: str, level: NormalizedValue) -> None:
        """
        Set channel fader level.

        Args:
            channel_id: The channel identifier
            level: Normalized fader level (0.0 = -inf, 1.0 = +10dB typically)
        """

    @hookspec
    def set_mute(self, channel_id: str, muted: bool) -> None:
        """
        Set channel mute state.

        Args:
            channel_id: The channel identifier
            muted: True to mute, False to unmute
        """

    @hookspec
    def set_solo(self, channel_id: str, soloed: bool) -> None:
        """
        Set channel solo state.

        Args:
            channel_id: The channel identifier
            soloed: True to solo, False to unsolo
        """

    @hookspec
    def set_pan(self, channel_id: str, pan: PanValue) -> None:
        """
        Set channel pan position.

        Args:
            channel_id: The channel identifier
            pan: Pan position (-1.0 = full left, 0.0 = center, 1.0 = full right)
        """

    # =========================================================================
    # Routing
    # =========================================================================

    @hookspec
    def set_main_assign(self, channel_id: str, assigned: bool) -> None:
        """
        Assign/unassign channel to main mix.

        Args:
            channel_id: The channel identifier
            assigned: True to assign to main, False to unassign
        """

    @hookspec
    def set_dca_assign(self, channel_id: str, dca_group: int, assigned: bool) -> None:
        """
        Assign/unassign channel to a DCA group.

        Args:
            channel_id: The channel identifier
            dca_group: DCA group number (1-indexed)
            assigned: True to assign, False to unassign
        """

    @hookspec
    def set_send_level(
        self, channel_id: str, send_id: str, level: NormalizedValue
    ) -> None:
        """
        Set aux/bus send level.

        Args:
            channel_id: The source channel identifier
            send_id: The target aux/bus identifier
            level: Normalized send level
        """

    @hookspec
    def set_send_pan(self, channel_id: str, send_id: str, pan: PanValue) -> None:
        """
        Set aux/bus send pan (for stereo sends).

        Args:
            channel_id: The source channel identifier
            send_id: The target aux/bus identifier
            pan: Pan position
        """

    @hookspec
    def set_send_pre_post(self, channel_id: str, send_id: str, pre_fader: bool) -> None:
        """
        Set send to pre or post fader.

        Args:
            channel_id: The source channel identifier
            send_id: The target aux/bus identifier
            pre_fader: True for pre-fader, False for post-fader
        """

    # =========================================================================
    # EQ
    # =========================================================================

    @hookspec
    def set_eq_enabled(self, channel_id: str, enabled: bool) -> None:
        """Enable/disable channel EQ."""

    @hookspec
    def set_eq_band(self, channel_id: str, band_index: int, band: EQBand) -> None:
        """
        Set EQ band parameters.

        Args:
            channel_id: The channel identifier
            band_index: EQ band index (0-based)
            band: EQBand configuration
        """

    # =========================================================================
    # Dynamics
    # =========================================================================

    @hookspec
    def set_compressor(self, channel_id: str, compressor: Compressor) -> None:
        """
        Set compressor parameters.

        Args:
            channel_id: The channel identifier
            compressor: Full compressor configuration
        """

    @hookspec
    def set_gate(self, channel_id: str, gate: Gate) -> None:
        """
        Set gate parameters.

        Args:
            channel_id: The channel identifier
            gate: Full gate configuration
        """

    # =========================================================================
    # Channel Configuration
    # =========================================================================

    @hookspec
    def set_channel_name(self, channel_id: str, name: str) -> None:
        """
        Set channel name/label.

        Args:
            channel_id: The channel identifier
            name: Channel name (may be truncated by hardware)
        """

    @hookspec
    def set_channel_color(self, channel_id: str, color: int) -> None:
        """
        Set channel scribble strip color.

        Args:
            channel_id: The channel identifier
            color: Color index (0-7 typically)
        """

    # =========================================================================
    # Scenes
    # =========================================================================

    @hookspec
    def recall_scene(self, scene_number: int) -> None:
        """
        Recall a scene from hardware memory.

        Args:
            scene_number: Scene number (1-indexed typically)
        """

    @hookspec
    def store_scene(self, scene_number: int, name: Optional[str] = None) -> None:
        """
        Store current state to a scene slot.

        Args:
            scene_number: Scene slot number
            name: Optional scene name
        """

    @hookspec
    def get_scene_list(self) -> list[tuple[int, str]]:
        """
        Get list of available scenes.

        Returns:
            List of (scene_number, scene_name) tuples
        """

    # =========================================================================
    # Metering
    # =========================================================================

    @hookspec
    def start_meters(self, interval_ms: int = 50) -> None:
        """
        Start meter data streaming.

        Args:
            interval_ms: Update interval in milliseconds
        """

    @hookspec
    def stop_meters(self) -> None:
        """Stop meter data streaming."""

    @hookspec
    def get_meters(self) -> dict[str, float]:
        """
        Get current meter values.

        Returns:
            Dict mapping channel_id to normalized meter level
        """

    # =========================================================================
    # Event Callbacks (called by plugins)
    # =========================================================================

    @hookspec
    def on_parameter_change(self, change: ParameterChange) -> None:
        """
        Called when a parameter changes on the hardware.

        Plugins call this when they receive parameter updates from
        the mixer (e.g., someone moves a physical fader).

        Args:
            change: The parameter change event
        """

    @hookspec
    def on_meter_update(self, meters: dict[str, float]) -> None:
        """
        Called when new meter data is received.

        Args:
            meters: Dict mapping channel_id to meter level
        """

    @hookspec
    def on_connection_status(
        self, connected: bool, error: Optional[str] = None
    ) -> None:
        """
        Called when connection status changes.

        Args:
            connected: True if connected, False if disconnected
            error: Optional error message if disconnected due to error
        """


class ProtocolAdapterSpec:
    """
    Protocol adapter specification.

    Protocol adapters handle the low-level communication (MIDI, OSC, TCP).
    Board plugins use these adapters rather than implementing protocols directly.
    """

    @hookspec
    def send(self, message: bytes) -> None:
        """Send raw message bytes."""

    @hookspec
    def receive(self) -> Optional[bytes]:
        """Receive raw message bytes (non-blocking)."""

    @hookspec
    def set_callback(self, callback: callable) -> None:
        """Set callback for incoming messages."""

    @hookspec
    def open(self, connection_string: str) -> bool:
        """Open connection. Returns True on success."""

    @hookspec
    def close(self) -> None:
        """Close connection."""
