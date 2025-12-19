"""Base Board Plugin

Abstract base class for board plugins that provides common functionality
and establishes the pattern for implementing new mixer support.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
from ludwig.hookspecs import hookimpl
from ludwig.models import (
    Channel,
    ChannelType,
    MixerState,
    DeviceInfo,
    DeviceCapabilities,
    ConnectionProtocol,
    ConnectionStatus,
    ParameterChange,
    NormalizedValue,
    PanValue,
    EQBand,
    Compressor,
    Gate,
)


class BoardPlugin(ABC):
    """
    Abstract base class for mixer board plugins.

    Subclasses must implement the abstract methods to provide
    board-specific protocol handling and value translation.

    Example usage:
        class MyMixer(BoardPlugin):
            MANUFACTURER = "Acme"
            MODEL = "ProMix 24"
            PROTOCOL = ConnectionProtocol.MIDI

            def _translate_fader_to_hardware(self, level: float) -> int:
                return int(level * 127)  # MIDI 7-bit

            # ... implement other abstract methods
    """

    # Subclasses should override these
    MANUFACTURER: str = "Unknown"
    MODEL: str = "Unknown"
    PROTOCOL: ConnectionProtocol = ConnectionProtocol.MIDI

    def __init__(
        self,
        connection_string: str,
        on_parameter_change: Optional[Callable[[ParameterChange], None]] = None,
        on_meter_update: Optional[Callable[[dict[str, float]], None]] = None,
        on_connection_status: Optional[Callable[[bool, Optional[str]], None]] = None,
    ):
        """
        Initialize the board plugin.

        Args:
            connection_string: Protocol-specific connection info
                MIDI: port name, e.g., "QU-24 MIDI 1"
                OSC: "host:port", e.g., "192.168.1.100:10023"
            on_parameter_change: Callback for hardware parameter changes
            on_meter_update: Callback for meter data
            on_connection_status: Callback for connection status changes
        """
        self.connection_string = connection_string
        self._on_parameter_change = on_parameter_change
        self._on_meter_update = on_meter_update
        self._on_connection_status = on_connection_status

        self._connected = False
        self._state: Optional[MixerState] = None
        self._capabilities = self._get_capabilities()

    # =========================================================================
    # Abstract Methods - Subclasses MUST implement
    # =========================================================================

    @abstractmethod
    def _get_capabilities(self) -> DeviceCapabilities:
        """Return the device capabilities."""
        pass

    @abstractmethod
    def _connect_hardware(self) -> bool:
        """Establish hardware connection. Return True on success."""
        pass

    @abstractmethod
    def _disconnect_hardware(self) -> None:
        """Close hardware connection."""
        pass

    @abstractmethod
    def _send_fader(
        self, channel_index: int, channel_type: ChannelType, level: int
    ) -> None:
        """Send fader value to hardware (translated value)."""
        pass

    @abstractmethod
    def _send_mute(
        self, channel_index: int, channel_type: ChannelType, muted: bool
    ) -> None:
        """Send mute state to hardware."""
        pass

    @abstractmethod
    def _send_pan(
        self, channel_index: int, channel_type: ChannelType, pan: int
    ) -> None:
        """Send pan value to hardware (translated value)."""
        pass

    @abstractmethod
    def _request_full_state(self) -> None:
        """Request full state dump from hardware."""
        pass

    # =========================================================================
    # Value Translation - Subclasses should override as needed
    # =========================================================================

    def _translate_fader_to_hardware(self, level: NormalizedValue) -> int:
        """Convert normalized fader (0.0-1.0) to hardware value."""
        return int(level * 127)  # Default: MIDI 7-bit

    def _translate_fader_from_hardware(self, value: int) -> NormalizedValue:
        """Convert hardware fader value to normalized."""
        return value / 127.0

    def _translate_pan_to_hardware(self, pan: PanValue) -> int:
        """Convert normalized pan (-1.0 to 1.0) to hardware value."""
        return int((pan + 1.0) * 63.5)  # 0-127, 64=center

    def _translate_pan_from_hardware(self, value: int) -> PanValue:
        """Convert hardware pan value to normalized."""
        return (value / 63.5) - 1.0

    def _channel_id_to_index(self, channel_id: str) -> tuple[int, ChannelType]:
        """
        Convert channel ID string to hardware index and type.

        Args:
            channel_id: e.g., "input_1", "aux_3", "main"

        Returns:
            Tuple of (hardware_index, channel_type)
        """
        parts = channel_id.rsplit("_", 1)
        type_str = parts[0]
        index = int(parts[1]) if len(parts) > 1 else 0

        type_map = {
            "input": ChannelType.INPUT,
            "ch": ChannelType.INPUT,
            "aux": ChannelType.AUX,
            "bus": ChannelType.BUS,
            "fx": ChannelType.FX_RETURN,
            "fxsend": ChannelType.FX_SEND,
            "dca": ChannelType.DCA,
            "matrix": ChannelType.MATRIX,
            "main": ChannelType.MAIN,
        }

        return index, type_map.get(type_str, ChannelType.INPUT)

    # =========================================================================
    # Hook Implementations
    # =========================================================================

    @hookimpl
    def connect(self) -> bool:
        """Establish connection to the mixer hardware."""
        try:
            success = self._connect_hardware()
            self._connected = success
            if self._on_connection_status:
                self._on_connection_status(
                    success, None if success else "Connection failed"
                )
            return success
        except Exception as e:
            self._connected = False
            if self._on_connection_status:
                self._on_connection_status(False, str(e))
            return False

    @hookimpl
    def disconnect(self) -> None:
        """Close connection to the mixer hardware."""
        self._disconnect_hardware()
        self._connected = False
        if self._on_connection_status:
            self._on_connection_status(False, None)

    @hookimpl
    def is_connected(self) -> bool:
        """Check if currently connected to hardware."""
        return self._connected

    @hookimpl
    def get_device_info(self) -> DeviceInfo:
        """Get information about the connected device."""
        return DeviceInfo(
            id=f"{self.MANUFACTURER}_{self.MODEL}".lower().replace(" ", "_"),
            name=f"{self.MANUFACTURER} {self.MODEL}",
            manufacturer=self.MANUFACTURER,
            model=self.MODEL,
            protocol=self.PROTOCOL,
            connection_string=self.connection_string,
            status=(
                ConnectionStatus.CONNECTED
                if self._connected
                else ConnectionStatus.DISCONNECTED
            ),
            capabilities=self._capabilities,
        )

    @hookimpl
    def set_fader(self, channel_id: str, level: NormalizedValue) -> None:
        """Set channel fader level."""
        index, ch_type = self._channel_id_to_index(channel_id)
        hw_value = self._translate_fader_to_hardware(level)
        self._send_fader(index, ch_type, hw_value)

        # Update local state
        if self._state and channel_id in self._state.channels:
            self._state.channels[channel_id].fader = level

    @hookimpl
    def set_mute(self, channel_id: str, muted: bool) -> None:
        """Set channel mute state."""
        index, ch_type = self._channel_id_to_index(channel_id)
        self._send_mute(index, ch_type, muted)

        if self._state and channel_id in self._state.channels:
            self._state.channels[channel_id].mute = muted

    @hookimpl
    def set_pan(self, channel_id: str, pan: PanValue) -> None:
        """Set channel pan position."""
        index, ch_type = self._channel_id_to_index(channel_id)
        hw_value = self._translate_pan_to_hardware(pan)
        self._send_pan(index, ch_type, hw_value)

        if self._state and channel_id in self._state.channels:
            self._state.channels[channel_id].pan = pan

    @hookimpl
    def sync_state(self) -> MixerState:
        """Request full state sync from hardware."""
        self._request_full_state()
        # Note: Actual state will be populated via callbacks as hardware responds
        if not self._state:
            self._state = MixerState(
                device=self.get_device_info(),
                channels=self._create_default_channels(),
            )
        return self._state

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _create_default_channels(self) -> dict[str, Channel]:
        """Create default channel structure based on capabilities."""
        channels = {}

        # Input channels
        for i in range(1, self._capabilities.input_channels + 1):
            ch_id = f"input_{i}"
            channels[ch_id] = Channel(
                id=ch_id,
                index=i,
                channel_type=ChannelType.INPUT,
                name=f"Ch {i}",
            )

        # Aux channels
        for i in range(1, self._capabilities.aux_channels + 1):
            ch_id = f"aux_{i}"
            channels[ch_id] = Channel(
                id=ch_id,
                index=i,
                channel_type=ChannelType.AUX,
                name=f"Aux {i}",
            )

        # FX Returns
        for i in range(1, self._capabilities.fx_returns + 1):
            ch_id = f"fx_{i}"
            channels[ch_id] = Channel(
                id=ch_id,
                index=i,
                channel_type=ChannelType.FX_RETURN,
                name=f"FX {i}",
            )

        # Main
        channels["main"] = Channel(
            id="main",
            index=0,
            channel_type=ChannelType.MAIN,
            name="Main",
        )

        return channels

    def _emit_parameter_change(
        self, channel_id: str, parameter: str, value: Any, source: str = "hardware"
    ) -> None:
        """Emit a parameter change event."""
        if self._on_parameter_change:
            change = ParameterChange(
                channel_id=channel_id,
                parameter=parameter,
                value=value,
                source=source,
            )
            self._on_parameter_change(change)

    def _emit_meter_update(self, meters: dict[str, float]) -> None:
        """Emit meter update event."""
        if self._on_meter_update:
            self._on_meter_update(meters)
