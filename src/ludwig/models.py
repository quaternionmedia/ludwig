"""Ludwig Models

Pydantic models for unified mixer state representation.
These models provide a protocol-agnostic abstraction layer.
"""

from enum import Enum, IntEnum
from typing import Annotated, Optional
from pydantic import BaseModel, Field, conint, confloat


# =============================================================================
# Enums
# =============================================================================


class ChannelType(str, Enum):
    """Type of audio channel"""

    INPUT = "input"
    AUX = "aux"
    BUS = "bus"
    FX_RETURN = "fx_return"
    FX_SEND = "fx_send"
    DCA = "dca"
    MATRIX = "matrix"
    MAIN = "main"
    STEREO = "stereo"


class ChannelColor(IntEnum):
    """Standard channel colors (8 options)"""

    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    PURPLE = 5
    CYAN = 6
    WHITE = 7


class CompressorType(IntEnum):
    """Compressor algorithm types"""

    SOFT = 0
    MEDIUM = 1
    HARD = 2
    BRICK = 3


class EQBandType(str, Enum):
    """EQ band filter types"""

    LOW_SHELF = "low_shelf"
    LOW_CUT = "low_cut"
    PARAMETRIC = "parametric"
    HIGH_SHELF = "high_shelf"
    HIGH_CUT = "high_cut"


class ConnectionProtocol(str, Enum):
    """Supported connection protocols"""

    MIDI = "midi"
    OSC = "osc"
    TCP = "tcp"


class ConnectionStatus(str, Enum):
    """Device connection status"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


# =============================================================================
# Value Types (Normalized 0.0-1.0 or dB)
# =============================================================================

NormalizedValue = Annotated[float, Field(ge=0.0, le=1.0)]
PanValue = Annotated[float, Field(ge=-1.0, le=1.0)]  # -1=L, 0=C, 1=R
DecibelValue = Annotated[float, Field(ge=-144.0, le=24.0)]
FrequencyHz = Annotated[float, Field(ge=20.0, le=20000.0)]
QValue = Annotated[float, Field(ge=0.1, le=20.0)]


# =============================================================================
# Component Models
# =============================================================================


class EQBand(BaseModel):
    """Single EQ band configuration"""

    enabled: bool = True
    band_type: EQBandType = EQBandType.PARAMETRIC
    frequency: FrequencyHz = 1000.0
    gain: DecibelValue = 0.0
    q: QValue = 1.0


class Equalizer(BaseModel):
    """Multi-band equalizer configuration"""

    enabled: bool = True
    bands: list[EQBand] = Field(
        default_factory=lambda: [
            EQBand(band_type=EQBandType.LOW_SHELF, frequency=80.0),
            EQBand(band_type=EQBandType.PARAMETRIC, frequency=400.0),
            EQBand(band_type=EQBandType.PARAMETRIC, frequency=2000.0),
            EQBand(band_type=EQBandType.HIGH_SHELF, frequency=8000.0),
        ]
    )


class Compressor(BaseModel):
    """Dynamics compressor configuration"""

    enabled: bool = False
    comp_type: CompressorType = CompressorType.MEDIUM
    threshold: DecibelValue = -20.0
    ratio: Annotated[float, Field(ge=1.0, le=100.0)] = 4.0
    attack_ms: Annotated[float, Field(ge=0.1, le=300.0)] = 10.0
    release_ms: Annotated[float, Field(ge=10.0, le=2000.0)] = 100.0
    knee: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5  # 0=hard, 1=soft
    makeup_gain: DecibelValue = 0.0


class Gate(BaseModel):
    """Noise gate configuration"""

    enabled: bool = False
    threshold: DecibelValue = -40.0
    range: DecibelValue = -80.0
    attack_ms: Annotated[float, Field(ge=0.01, le=100.0)] = 0.5
    hold_ms: Annotated[float, Field(ge=0.0, le=2000.0)] = 50.0
    release_ms: Annotated[float, Field(ge=10.0, le=2000.0)] = 200.0


class Send(BaseModel):
    """Aux/Bus send configuration"""

    target_id: str  # ID of the aux/bus channel
    level: NormalizedValue = 0.0
    pan: PanValue = 0.0
    pre_fader: bool = False
    enabled: bool = True


# =============================================================================
# Channel Model
# =============================================================================


class Channel(BaseModel):
    """
    Universal channel representation.

    All values are normalized (0.0-1.0) or in standard units (dB, Hz).
    Board plugins translate these to/from protocol-specific values.
    """

    # Identity
    id: str  # Unique identifier (e.g., "ch_1", "aux_2", "main_lr")
    index: int  # Hardware channel number
    channel_type: ChannelType = ChannelType.INPUT
    name: str = ""
    color: ChannelColor = ChannelColor.WHITE

    # Fader Section
    fader: NormalizedValue = 0.0
    mute: bool = False
    solo: bool = False
    pan: PanValue = 0.0

    # Routing
    assigned_to_main: bool = True
    dca_groups: list[int] = Field(default_factory=list)  # DCA group numbers
    mute_groups: list[int] = Field(default_factory=list)

    # Processing
    eq: Equalizer = Field(default_factory=Equalizer)
    compressor: Compressor = Field(default_factory=Compressor)
    gate: Gate = Field(default_factory=Gate)

    # Sends (aux/bus)
    sends: list[Send] = Field(default_factory=list)

    # Metering (read-only from hardware)
    meter_level: NormalizedValue = 0.0
    gain_reduction: NormalizedValue = 0.0


# =============================================================================
# Scene / Snapshot Models
# =============================================================================


class Scene(BaseModel):
    """A complete mixer state snapshot"""

    id: str
    name: str
    description: str = ""
    channels: list[Channel] = Field(default_factory=list)
    created_at: Optional[str] = None
    modified_at: Optional[str] = None


class SceneRecallScope(BaseModel):
    """Define what elements to recall from a scene"""

    faders: bool = True
    mutes: bool = True
    eq: bool = True
    dynamics: bool = True
    routing: bool = True
    names: bool = False


# =============================================================================
# Device / Connection Models
# =============================================================================


class DeviceCapabilities(BaseModel):
    """Describes what a mixer supports"""

    input_channels: int = 0
    aux_channels: int = 0
    fx_returns: int = 0
    fx_sends: int = 0
    dca_groups: int = 0
    mute_groups: int = 0
    matrices: int = 0
    scenes: int = 0

    has_eq: bool = True
    eq_bands: int = 4
    has_compressor: bool = True
    has_gate: bool = True
    has_pan: bool = True

    supports_meters: bool = True
    supports_names: bool = True
    supports_colors: bool = True


class DeviceInfo(BaseModel):
    """Information about a connected mixer device"""

    id: str
    name: str
    manufacturer: str = ""
    model: str = ""
    firmware_version: str = ""

    protocol: ConnectionProtocol
    connection_string: str  # e.g., "midi:QU-24 MIDI 1" or "osc:192.168.1.100:10023"
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED

    capabilities: DeviceCapabilities = Field(default_factory=DeviceCapabilities)


# =============================================================================
# Mixer State Model
# =============================================================================


class MixerState(BaseModel):
    """
    Complete mixer state.

    This is the central state object that the backend maintains
    and synchronizes with both hardware and connected clients.
    """

    device: DeviceInfo
    channels: dict[str, Channel] = Field(default_factory=dict)
    current_scene: Optional[str] = None

    # Meter values (updated frequently, may be separate stream)
    meters: dict[str, float] = Field(default_factory=dict)

    def get_channels_by_type(self, channel_type: ChannelType) -> list[Channel]:
        """Get all channels of a specific type"""
        return [ch for ch in self.channels.values() if ch.channel_type == channel_type]

    def get_input_channels(self) -> list[Channel]:
        """Get all input channels"""
        return self.get_channels_by_type(ChannelType.INPUT)

    def get_aux_channels(self) -> list[Channel]:
        """Get all aux/bus channels"""
        return self.get_channels_by_type(ChannelType.AUX)


# =============================================================================
# API Message Models
# =============================================================================


class ParameterChange(BaseModel):
    """A single parameter change event"""

    channel_id: str
    parameter: str  # e.g., "fader", "mute", "eq.bands.0.gain"
    value: float | bool | str | int
    source: str = "api"  # "api", "hardware", "scene"


class BatchParameterChange(BaseModel):
    """Multiple parameter changes in one message"""

    changes: list[ParameterChange]


class MeterUpdate(BaseModel):
    """Meter level update (frequent, lightweight)"""

    levels: dict[str, float]  # channel_id -> normalized level
    gain_reductions: dict[str, float] = Field(default_factory=dict)
