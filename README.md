# Ludwig

Remote audio mixing workstation - control sound boards via MIDI/OSC with a unified web interface.

## Features

- **Universal mixer control** - Single API for multiple mixer brands (Behringer XAir, Allen & Heath QU/GLD, and more)
- **Real-time WebSocket API** - Low-latency bidirectional control
- **Plugin architecture** - Easy to add support for new mixers
- **Normalized values** - All parameters use 0.0-1.0 scale, translated to hardware-specific values

## Installation

```bash
# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

## Quick Start

### Python API (Direct Hardware Control)

```python
from ludwig.boards import XAirPlugin

# Create a callback to handle hardware changes
def on_parameter_change(change):
    print(f"Hardware changed: {change.channel_id}.{change.parameter} = {change.value}")

def on_connection_status(connected, error):
    if connected:
        print("Connected to mixer!")
    else:
        print(f"Disconnected: {error}")

# Initialize the mixer plugin
mixer = XAirPlugin(
    connection_string="X18",  # MIDI port name
    on_parameter_change=on_parameter_change,
    on_connection_status=on_connection_status,
)

# Connect to the hardware
if mixer.connect():
    print(f"Connected to {mixer.MANUFACTURER} {mixer.MODEL}")

    # Control channels using normalized values (0.0 - 1.0)
    mixer.set_fader("input_1", 0.75)      # Set channel 1 to 75%
    mixer.set_fader("input_2", 0.5)       # Set channel 2 to 50%
    mixer.set_fader("main", 0.8)          # Set main fader to 80%

    # Mute/unmute channels
    mixer.set_mute("input_3", True)       # Mute channel 3
    mixer.set_mute("input_3", False)      # Unmute channel 3

    # Pan control (-1.0 = full left, 0.0 = center, 1.0 = full right)
    mixer.set_pan("input_1", -0.5)        # Pan channel 1 slightly left
    mixer.set_pan("input_2", 0.0)         # Center channel 2

    # Control aux sends and FX returns
    mixer.set_fader("aux_1", 0.6)         # Aux 1 master at 60%
    mixer.set_fader("fx_1", 0.4)          # FX Return 1 at 40%

    # Get device info
    info = mixer.get_device_info()
    print(f"Device: {info.name}")
    print(f"Inputs: {info.capabilities.input_channels}")
    print(f"Aux sends: {info.capabilities.aux_channels}")

    # Disconnect when done
    mixer.disconnect()
```

### Channel ID Reference

| Channel Type   | ID Format  | Examples               |
| -------------- | ---------- | ---------------------- |
| Input channels | `input_N`  | `input_1`, `input_16`  |
| Aux/Bus        | `aux_N`    | `aux_1`, `aux_6`       |
| FX Returns     | `fx_N`     | `fx_1`, `fx_4`         |
| FX Sends       | `fxsend_N` | `fxsend_1`, `fxsend_4` |
| Main output    | `main`     | `main`                 |

### Handling Hardware Changes

The plugin receives MIDI messages when someone adjusts the physical mixer:

```python
from ludwig.boards import XAirPlugin
from ludwig.models import ParameterChange

def on_hardware_change(change: ParameterChange):
    """Called when a fader/mute/pan changes on the hardware."""
    print(f"[{change.source}] {change.channel_id}.{change.parameter} = {change.value}")

    # React to changes
    if change.parameter == "fader":
        # Update your UI, database, etc.
        pass
    elif change.parameter == "mute":
        if change.value:
            print(f"{change.channel_id} was muted")
    elif change.parameter == "pan":
        # change.value is -1.0 to 1.0
        pass

mixer = XAirPlugin(
    connection_string="X-AIR",
    on_parameter_change=on_hardware_change,
)
mixer.connect()

# Keep running to receive callbacks
import time
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    mixer.disconnect()
```

### Web Server (REST + WebSocket)

```bash
# Start the Ludwig API server
ludwig

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

Example API calls:

```bash
# List connected devices
curl http://localhost:8000/api/devices

# Get mixer state
curl http://localhost:8000/api/mixer/state

# Set a fader
curl -X POST "http://localhost:8000/api/mixer/channels/input_1/fader?level=0.75"

# Mute a channel
curl -X POST "http://localhost:8000/api/mixer/channels/input_1/mute?muted=true"
```

### WebSocket Real-time Control

```javascript
const ws = new WebSocket('ws://localhost:8000/ws')

ws.onopen = () => {
  // Set fader
  ws.send(
    JSON.stringify({
      type: 'fader',
      channel_id: 'input_1',
      value: 0.75,
    })
  )

  // Toggle mute
  ws.send(
    JSON.stringify({
      type: 'mute',
      channel_id: 'input_2',
      value: true,
    })
  )
}

ws.onmessage = event => {
  const msg = JSON.parse(event.data)

  if (msg.type === 'state') {
    // Full mixer state received
    console.log('Channels:', msg.data.channels)
  } else if (msg.type === 'parameter') {
    // Single parameter changed
    console.log(`${msg.channel_id}.${msg.parameter} = ${msg.value}`)
  } else if (msg.type === 'meters') {
    // Meter levels (high frequency)
    console.log('Meters:', msg.levels)
  }
}
```

## Supported Mixers

| Manufacturer  | Model                   | Protocol | Status                   |
| ------------- | ----------------------- | -------- | ------------------------ |
| Behringer     | XR12, XR16, XR18, X Air | MIDI     | ✅ Ready                 |
| Allen & Heath | QU-16, QU-24, QU-32     | MIDI     | 🔄 Migration in progress |
| Allen & Heath | GLD                     | MIDI     | 🔄 Migration in progress |
| Behringer     | X32, M32                | OSC      | 📋 Planned               |

## Creating a Custom Board Plugin

```python
from ludwig.plugins.base import BoardPlugin
from ludwig.models import DeviceCapabilities, ChannelType, ConnectionProtocol

class MyMixerPlugin(BoardPlugin):
    MANUFACTURER = "MyBrand"
    MODEL = "ProMix 16"
    PROTOCOL = ConnectionProtocol.MIDI  # or OSC, TCP

    def _get_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            input_channels=16,
            aux_channels=4,
            fx_returns=2,
            fx_sends=2,
            scenes=50,
        )

    def _connect_hardware(self) -> bool:
        # Establish connection to your mixer
        # Return True on success
        pass

    def _disconnect_hardware(self) -> None:
        # Clean up connection
        pass

    def _send_fader(self, channel_index: int, channel_type: ChannelType, level: int) -> None:
        # Send fader value to hardware
        # `level` is already translated via _translate_fader_to_hardware()
        pass

    def _send_mute(self, channel_index: int, channel_type: ChannelType, muted: bool) -> None:
        # Send mute state to hardware
        pass

    def _send_pan(self, channel_index: int, channel_type: ChannelType, pan: int) -> None:
        # Send pan value to hardware
        pass

    def _request_full_state(self) -> None:
        # Request current state from hardware (if supported)
        pass
```

## Documentation

- [Project Roadmap](docs/planning/PROJECT_ROADMAP.md) - Development timeline and milestones
- [Frontend Specification](docs/planning/FRONTEND_SPEC.md) - Web UI design with Mithril.js
- [Next Steps](docs/planning/NEXT_STEPS.md) - Current status and priorities

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Start server in dev mode
ludwig
```

## License

MIT
