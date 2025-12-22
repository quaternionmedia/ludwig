"""Behringer XAir Series Plugin

Supports XR12, XR16, XR18, X Air series mixers via MIDI.

MIDI Channel Mapping:
    CH 1 (CC):  Faders
    CH 2 (CC):  Mutes
    CH 3 (CC):  Pan

CC Number Mapping:
    0-15:   Input Channels 1-16
    16:     AuxLineIn 17-18 / USB Recorder Playback (stereo)
    17-20:  FX1-4 Return (stereo)
    21-26:  Aux1-6 / Subgroup
    27-30:  FX1-4 Send
    31:     Main LR (stereo)
"""

from typing import Optional, Callable
from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import CONTROL_CHANGE
from rtmidi import API_UNIX_JACK

from ludwig.plugins.base import BoardPlugin
from ludwig.hookspecs import hookimpl
from ludwig.models import (
    ChannelType,
    DeviceCapabilities,
    ConnectionProtocol,
    ParameterChange,
    NormalizedValue,
    PanValue,
)


class XAirPlugin(BoardPlugin):
    """
    Behringer XAir series mixer plugin.

    Supports: XR12, XR16, XR18, X Air
    Protocol: MIDI (CC messages)
    """

    MANUFACTURER = "Behringer"
    MODEL = "XAir"
    PROTOCOL = ConnectionProtocol.MIDI

    # MIDI CC channels (0-indexed)
    _FADER_CHANNEL = 0  # CH 1
    _MUTE_CHANNEL = 1  # CH 2
    _PAN_CHANNEL = 2  # CH 3

    # CC number ranges
    _INPUT_CC_START = 0
    _INPUT_CC_END = 15
    _AUX_LINE_IN_CC = 16
    _FX_RETURN_CC_START = 17
    _FX_RETURN_CC_END = 20
    _AUX_CC_START = 21
    _AUX_CC_END = 26
    _FX_SEND_CC_START = 27
    _FX_SEND_CC_END = 30
    _MAIN_CC = 31

    def __init__(
        self,
        connection_string: str,
        on_parameter_change: Optional[Callable[[ParameterChange], None]] = None,
        on_meter_update: Optional[Callable[[dict[str, float]], None]] = None,
        on_connection_status: Optional[Callable[[bool, Optional[str]], None]] = None,
        client_name: str = "xair",
    ):
        self._client_name = client_name
        self._midi_out = None
        self._midi_in = None
        super().__init__(
            connection_string,
            on_parameter_change,
            on_meter_update,
            on_connection_status,
        )

    # =========================================================================
    # Abstract Method Implementations
    # =========================================================================

    def _get_capabilities(self) -> DeviceCapabilities:
        """XAir series capabilities."""
        return DeviceCapabilities(
            input_channels=16,
            aux_channels=6,
            fx_returns=4,
            fx_sends=4,
            dca_groups=4,
            mute_groups=4,
            matrices=0,
            scenes=64,
            has_eq=True,
            eq_bands=4,
            has_compressor=True,
            has_gate=True,
            has_pan=True,
            supports_meters=False,  # MIDI doesn't support meters on XAir
            supports_names=False,  # MIDI doesn't support names on XAir
            supports_colors=False,  # MIDI doesn't support colors on XAir
        )

    def _connect_hardware(self) -> bool:
        """Establish MIDI connection to XAir."""
        try:
            self._midi_out, _ = open_midioutput(
                self.connection_string,
                client_name=f"{self._client_name}-output",
                api=API_UNIX_JACK,
            )
            self._midi_in, _ = open_midiinput(
                self.connection_string,
                client_name=f"{self._client_name}-input",
                api=API_UNIX_JACK,
            )
            self._midi_in.ignore_types(sysex=False)
            self._midi_in.set_callback(self._handle_midi_input)
            return True
        except Exception as e:
            print(f"XAir connection failed: {e}")
            return False

    def _disconnect_hardware(self) -> None:
        """Close MIDI connections."""
        if self._midi_out:
            self._midi_out.close_port()
            self._midi_out = None
        if self._midi_in:
            self._midi_in.close_port()
            self._midi_in = None

    def _send_fader(
        self, channel_index: int, channel_type: ChannelType, level: int
    ) -> None:
        """Send fader value via MIDI CC."""
        cc_number = self._get_cc_number(channel_index, channel_type)
        if cc_number is not None:
            self._send_cc(self._FADER_CHANNEL, cc_number, level)

    def _send_mute(
        self, channel_index: int, channel_type: ChannelType, muted: bool
    ) -> None:
        """Send mute state via MIDI CC."""
        cc_number = self._get_cc_number(channel_index, channel_type)
        if cc_number is not None:
            self._send_cc(self._MUTE_CHANNEL, cc_number, 127 if muted else 0)

    def _send_pan(
        self, channel_index: int, channel_type: ChannelType, pan: int
    ) -> None:
        """Send pan value via MIDI CC."""
        cc_number = self._get_cc_number(channel_index, channel_type)
        if cc_number is not None:
            self._send_cc(self._PAN_CHANNEL, cc_number, pan)

    def _request_full_state(self) -> None:
        """XAir MIDI doesn't support state queries - no-op."""
        # MIDI protocol on XAir doesn't support requesting current state
        # State must be inferred from incoming CC messages or OSC
        pass

    # =========================================================================
    # XAir-Specific Helpers
    # =========================================================================

    def _send_cc(self, midi_channel: int, cc_number: int, value: int) -> None:
        """Send a MIDI Control Change message."""
        if self._midi_out:
            message = [CONTROL_CHANGE | midi_channel, cc_number, value]
            self._midi_out.send_message(message)

    def _get_cc_number(
        self, channel_index: int, channel_type: ChannelType
    ) -> Optional[int]:
        """
        Map channel index and type to MIDI CC number.

        Args:
            channel_index: 1-indexed channel number
            channel_type: Type of channel

        Returns:
            CC number (0-31) or None if invalid
        """
        if channel_type == ChannelType.INPUT:
            if 1 <= channel_index <= 16:
                return channel_index - 1  # CC 0-15
            elif channel_index == 17:
                return self._AUX_LINE_IN_CC  # CC 16 (stereo aux/USB)
        elif channel_type == ChannelType.FX_RETURN:
            if 1 <= channel_index <= 4:
                return self._FX_RETURN_CC_START + channel_index - 1  # CC 17-20
        elif channel_type == ChannelType.AUX:
            if 1 <= channel_index <= 6:
                return self._AUX_CC_START + channel_index - 1  # CC 21-26
        elif channel_type == ChannelType.FX_SEND:
            if 1 <= channel_index <= 4:
                return self._FX_SEND_CC_START + channel_index - 1  # CC 27-30
        elif channel_type == ChannelType.MAIN:
            return self._MAIN_CC  # CC 31

        return None

    def _cc_to_channel(self, cc_number: int) -> tuple[int, ChannelType]:
        """
        Map CC number back to channel index and type.

        Returns:
            Tuple of (1-indexed channel number, channel type)
        """
        if 0 <= cc_number <= 15:
            return cc_number + 1, ChannelType.INPUT
        elif cc_number == 16:
            return 17, ChannelType.INPUT  # Aux Line In
        elif 17 <= cc_number <= 20:
            return cc_number - 16, ChannelType.FX_RETURN
        elif 21 <= cc_number <= 26:
            return cc_number - 20, ChannelType.AUX
        elif 27 <= cc_number <= 30:
            return cc_number - 26, ChannelType.FX_SEND
        elif cc_number == 31:
            return 0, ChannelType.MAIN
        return 0, ChannelType.INPUT

    def _handle_midi_input(self, event, data=None):
        """Handle incoming MIDI messages from the mixer."""
        message, deltatime = event

        if len(message) >= 3:
            status = message[0]
            cc_number = message[1]
            value = message[2]

            # Check if it's a CC message
            if (status & 0xF0) == CONTROL_CHANGE:
                midi_channel = status & 0x0F
                channel_index, channel_type = self._cc_to_channel(cc_number)

                # Determine parameter based on MIDI channel
                if midi_channel == self._FADER_CHANNEL:
                    parameter = "fader"
                    normalized_value = self._translate_fader_from_hardware(value)
                elif midi_channel == self._MUTE_CHANNEL:
                    parameter = "mute"
                    normalized_value = value > 63
                elif midi_channel == self._PAN_CHANNEL:
                    parameter = "pan"
                    normalized_value = self._translate_pan_from_hardware(value)
                else:
                    return

                # Build channel ID
                type_prefix = {
                    ChannelType.INPUT: "input",
                    ChannelType.AUX: "aux",
                    ChannelType.FX_RETURN: "fx",
                    ChannelType.FX_SEND: "fxsend",
                    ChannelType.MAIN: "main",
                }
                prefix = type_prefix.get(channel_type, "input")
                if channel_type == ChannelType.MAIN:
                    channel_id = "main"
                else:
                    channel_id = f"{prefix}_{channel_index}"

                # Emit parameter change
                self._emit_parameter_change(
                    channel_id, parameter, normalized_value, source="hardware"
                )

    # =========================================================================
    # Additional XAir-Specific Methods
    # =========================================================================

    @hookimpl
    def set_send_level(
        self, channel_id: str, send_id: str, level: NormalizedValue
    ) -> None:
        """
        Set aux/FX send level.

        Note: XAir MIDI protocol doesn't support per-channel send levels.
        This is a limitation of the MIDI implementation - use OSC for full control.
        """
        # XAir MIDI only supports global aux fader control (CC 21-30)
        # Per-channel sends require OSC protocol
        pass


# Legacy alias for backwards compatibility
XAir = XAirPlugin
