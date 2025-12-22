# Ludwig - Next Steps & Recommendations

## What We've Built So Far

### 1. Project Roadmap ([PROJECT_ROADMAP.md](PROJECT_ROADMAP.md))

- Complete 14-week development timeline
- 6 phases from core architecture to deployment
- Risk assessment and success metrics
- Feature prioritization (P0/P1/P2)

### 2. Pydantic Models ([src/ludwig/models.py](../../src/ludwig/models.py))

- Protocol-agnostic state representation
- `Channel`, `MixerState`, `DeviceInfo` models
- Processing models: `Equalizer`, `Compressor`, `Gate`
- API message models for WebSocket communication

### 3. Enhanced Hook Specifications ([src/ludwig/hookspecs.py](../../src/ludwig/hookspecs.py))

- State-aware `MixerSpec` with normalized values
- Connection lifecycle hooks
- Full parameter control (fader, mute, pan, EQ, dynamics)
- Scene and meter management hooks
- `ProtocolAdapterSpec` for MIDI/OSC abstraction

### 4. Base Plugin Architecture ([src/ludwig/plugins/base.py](../../src/ludwig/plugins/base.py))

- Abstract `BoardPlugin` base class
- Value translation methods (normalized ↔ hardware)
- Hook implementations with state tracking
- Template for new board implementations

### 5. XAir Board Plugin ([src/ludwig/boards/xair.py](../../src/ludwig/boards/xair.py)) ✅ MIGRATED

- Full implementation using new `BoardPlugin` architecture
- MIDI CC mapping for faders, mutes, pan
- Bidirectional MIDI input handling
- Normalized value translation (0.0-1.0)
- Channel type routing (input, aux, FX, main)

### 6. FastAPI Server ([src/ludwig/server/](../../src/ludwig/server/))

- REST endpoints for device/channel management
- WebSocket for real-time bidirectional updates
- Meter broadcasting infrastructure
- State manager for synchronized state

### 7. Frontend Specification ([FRONTEND_SPEC.md](FRONTEND_SPEC.md))

- **Mithril.js** with **Meiosis pattern** for state management
- Component library (Fader, Meter, Knob, ChannelStrip)
- View layouts (Channel Strip, Detail, Send Matrix, Scenes)
- WebSocket integration with streams
- Performance and accessibility guidelines

---

## Immediate Next Steps (This Week)

### 1. ✅ Validate Models (Complete)

```bash
cd /home/harpo/ludwig
uv sync  # Install dependencies
python -c "from ludwig.models import MixerState, Channel; print('Models OK')"
```

### 2. ✅ XAir Board Migration (Complete)

The XAir board has been fully migrated to the new `BoardPlugin` architecture.
See [src/ludwig/boards/xair.py](../../src/ludwig/boards/xair.py)

### 3. Migrate Remaining Board Plugins

Refactor `Qu24` and `GLD` to use the new `BoardPlugin` base:

```python
# Example: src/ludwig/boards/qu24.py
from ludwig.plugins.base import BoardPlugin
from ludwig.models import DeviceCapabilities, ChannelType, ConnectionProtocol

class Qu24Plugin(BoardPlugin):
    MANUFACTURER = "Allen & Heath"
    MODEL = "QU-24"
    PROTOCOL = ConnectionProtocol.MIDI

    def _get_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            input_channels=24,
            aux_channels=10,
            fx_returns=4,
            fx_sends=4,
            scenes=100,
        )

    # ... implement abstract methods
```

### 4. Test API Server

```bash
# Start server
ludwig

# Test endpoints
curl http://localhost:8000/docs  # OpenAPI docs
curl http://localhost:8000/api/devices
```

### 5. Set Up Frontend Project

```bash
# Create Mithril.js project with Vite
mkdir frontend && cd frontend
npm init -y
npm install mithril mithril-stream
npm install -D vite tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Create entry point
echo 'import m from "mithril"
m.mount(document.body, { view: () => m("h1", "Ludwig") })' > src/app.js
```

---

## Short-Term Priorities (Weeks 1-4)

| Priority | Task                                    | Effort | Status      |
| -------- | --------------------------------------- | ------ | ----------- |
| 🟢 Done  | Migrate XAir plugin to new architecture | 2 days | ✅ Complete |
| 🔴 High  | Migrate Qu24 plugin to new architecture | 2 days | Not Started |
| 🔴 High  | Migrate GLD plugin to new architecture  | 2 days | Not Started |
| 🔴 High  | Wire StateManager to board plugins      | 1 day  | Not Started |
| 🔴 High  | Set up Mithril.js frontend project      | 1 day  | Not Started |
| 🔴 High  | Create Fader + Meter components         | 3 days | Not Started |
| 🟡 Med   | Add meter subscription to hardware      | 2 days | Not Started |
| 🟡 Med   | Implement scene recall flow             | 2 days | Not Started |
| 🟢 Low   | Add OSC protocol adapter                | 3 days | Not Started |

---

## Technical Recommendations

### 1. **Protocol Adapter Pattern**

Keep MIDI/OSC/TCP implementations separate from board logic:

```python
class MidiAdapter(ProtocolAdapter):
    def send(self, message: bytes) -> None:
        self.port.send_message(list(message))

class OscAdapter(ProtocolAdapter):
    def send(self, message: bytes) -> None:
        # OSC uses address patterns
        self.client.send_message(self.address, list(message))
```

### 2. **State Synchronization Strategy**

- Server maintains authoritative state
- Hardware changes propagate: Hardware → Plugin → State → WebSocket → All Clients
- UI changes propagate: Client → WebSocket → State → Plugin → Hardware → Echo to other clients
- Use sequence numbers to handle out-of-order messages

### 3. **Meter Optimization**

- Meters update at 20-50Hz, separate from parameter state
- Use binary WebSocket frames for meter data (not JSON)
- Consider SharedArrayBuffer for multi-client scenarios

### 4. **Plugin Discovery**

Use entry points for auto-discovery of board plugins:

```toml
# pyproject.toml
[project.entry-points."ludwig.boards"]
qu24 = "ludwig.boards.qu24:Qu24Plugin"
gld = "ludwig.boards.gld:GldPlugin"
x32 = "ludwig_x32:X32Plugin"  # Third-party package
```

### 5. **Testing Strategy**

- Unit tests for models and value translation
- Mock hardware for integration tests
- Use `pytest-asyncio` for API tests
- Use `ospec` (Mithril's test runner) for frontend unit tests
- Playwright for frontend E2E tests

---

## Architecture Evolution Path

```
Phase 1 (Now)           Phase 2 (Month 2)         Phase 3 (Month 3+)
─────────────────       ─────────────────         ─────────────────
Single Device           Multi-Device              Advanced Features
│                       │                         │
├── 1 WebSocket         ├── Device routing        ├── Custom layouts
├── In-memory state     ├── Redis state store     ├── User accounts
├── JSON meters         ├── Binary meters         ├── Cloud sync
└── Basic UI            └── Full mixer UI         └── Plugin marketplace
```

---

## Questions to Resolve

1. **Deployment model**: Single-user local? Multi-user cloud? Both?
2. **Offline support**: Should scenes be editable without hardware connected?
3. **MIDI learn**: Allow mapping control surfaces to any parameter?
4. **Multi-device**: Link multiple mixers with parameter sync?
5. **Mobile native**: Web-only (current plan with Mithril.js) or eventual native apps?
6. **Authentication**: Simple PIN? Full user accounts? None for local use?

---

## Resources

- **Mixing Station** (reference): https://mixingstation.app
- **python-rtmidi docs**: https://spotlightkid.github.io/python-rtmidi/
- **python-osc**: https://pypi.org/project/python-osc/
- **FastAPI WebSockets**: https://fastapi.tiangolo.com/advanced/websockets/
- **Mithril.js docs**: https://mithril.js.org/
- **Meiosis pattern**: https://meiosis.js.org/
- **Mithril Stream**: https://mithril.js.org/stream.html

---

## File Summary

```
ludwig/
├── docs/
│   └── planning/
│       ├── PROJECT_ROADMAP.md     # Full project plan
│       ├── FRONTEND_SPEC.md       # UI specification (Mithril/Meiosis)
│       └── NEXT_STEPS.md          # This document
├── src/ludwig/
│   ├── models.py                  # Pydantic models
│   ├── hookspecs.py               # Enhanced hook specs
│   ├── mixer.py                   # Original (to deprecate)
│   ├── plugins/
│   │   ├── __init__.py
│   │   └── base.py                # Base plugin class
│   ├── server/
│   │   ├── __init__.py
│   │   ├── api.py                 # FastAPI server
│   │   ├── state.py               # State manager
│   │   └── websocket.py           # WS manager
│   └── boards/
│       ├── xair.py                # ✅ Migrated to BoardPlugin
│       ├── qu24.py                # To migrate
│       ├── gld.py                 # To migrate
│       └── ...                    # Other boards
└── pyproject.toml                 # Updated dependencies
```

---

_Last Updated: December 20, 2025_

_Ready to start building! Next recommended step: Migrate Qu24 or set up the frontend project._
