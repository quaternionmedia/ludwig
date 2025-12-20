# Ludwig - Audio Mixing Workstation App

## Project Vision

Transform Ludwig from a simple MIDI mixer control library into a fully-fledged audio mixing workstation application, similar to "Mixing Station". The app will provide a unified web interface to control multiple types of sound boards via MIDI and OSC protocols.

---

## Current State Analysis

### Existing Architecture

- **Pluggy-based hook system** for defining mixer operations (`HookspecMarker`/`HookimplMarker`)
- **Base `Mixer` class** defining the interface spec (mute, fader, pan, compressor, etc.)
- **`Midi` class** handling RTMIDI connections, NRPN, and SysEx messaging
- **Board implementations**: Qu24, GLD, XAir, Command8, Generic

### Strengths

- Clean separation between interface spec and implementation
- Pydantic types for validation
- Support for multiple protocols (MIDI CC, NRPN, SysEx)

### Gaps to Address

- No API layer for remote control
- No state management (current mixer state)
- No OSC protocol support
- No real-time bidirectional communication
- No web frontend

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEB FRONTEND                                    │
│    Mithril.js SPA with Meiosis pattern + WebSocket real-time updates        │
│    - Channel strips, faders, meters                                          │
│    - EQ/Dynamics/FX editors                                                  │
│    - Scene management                                                        │
│    - Device configuration                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                              WebSocket + REST
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI SERVER                                     │
│    - REST endpoints for configuration/scenes                                 │
│    - WebSocket for real-time parameter updates & meters                      │
│    - Authentication & session management                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                              Internal API
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STATE MANAGER                                       │
│    - In-memory mixer state (channels, sends, FX)                            │
│    - State sync with hardware                                                │
│    - Event dispatching to connected clients                                  │
│    - Scene/snapshot storage (SQLite/JSON)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                          Pluggy Hook System
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROTOCOL ADAPTERS                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    MIDI     │  │     OSC     │  │   TCP/IP    │  │   Custom    │        │
│  │  Adapter    │  │   Adapter   │  │   Adapter   │  │   Adapter   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                         Hardware Abstraction
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BOARD PLUGINS                                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │  A&H    │ │ A&H GLD │ │Behringer│ │  Midas  │ │ Yamaha  │ │ Generic │  │
│  │  Qu24   │ │         │ │  XAir   │ │  M32    │ │   TF    │ │  MIDI   │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Project Phases & Milestones

### Phase 1: Core Architecture Refactor (Weeks 1-3)

**Goal:** Establish clean, extensible base architecture

| Task                                   | Priority | Estimate | Status      |
| -------------------------------------- | -------- | -------- | ----------- |
| Define Pydantic models for mixer state | High     | 3 days   | ✅ Complete |
| Refactor Mixer hookspec to use models  | High     | 2 days   | ✅ Complete |
| Create abstract Protocol adapter base  | High     | 2 days   | ✅ Complete |
| Implement StateManager class           | High     | 3 days   | ✅ Complete |
| Migrate XAir board to new architecture | High     | 2 days   | ✅ Complete |
| Add event bus for state changes        | Medium   | 2 days   | Not Started |
| Migrate Qu24/GLD boards                | Medium   | 3 days   | Not Started |
| Unit tests for core components         | High     | 3 days   | Not Started |

### Phase 2: FastAPI Server (Weeks 3-5)

**Goal:** Expose mixer control via REST & WebSocket

| Task                                  | Priority | Estimate | Status      |
| ------------------------------------- | -------- | -------- | ----------- |
| FastAPI project structure             | High     | 1 day    | ✅ Complete |
| REST endpoints for mixer operations   | High     | 3 days   | ✅ Complete |
| WebSocket endpoint for real-time sync | High     | 3 days   | ✅ Complete |
| WebSocket connection manager          | High     | 1 day    | ✅ Complete |
| Meter streaming via WebSocket         | High     | 2 days   | In Progress |
| Device discovery/connection endpoints | Medium   | 2 days   | Not Started |
| Authentication middleware             | Low      | 2 days   | Not Started |

### Phase 3: OSC Protocol Support (Weeks 5-6)

**Goal:** Add OSC as a first-class protocol

| Task                               | Priority | Estimate | Status      |
| ---------------------------------- | -------- | -------- | ----------- |
| OSC adapter implementation         | High     | 2 days   | Not Started |
| Behringer X32/M32 OSC board plugin | High     | 3 days   | Not Started |
| OSC parameter mapping system       | Medium   | 2 days   | Not Started |

### Phase 4: Frontend Foundation (Weeks 6-9)

**Goal:** Create basic but functional web UI

| Task                                | Priority | Estimate | Status      |
| ----------------------------------- | -------- | -------- | ----------- |
| Frontend project setup (Mithril.js) | High     | 1 day    | Not Started |
| Meiosis state management setup      | High     | 1 day    | Not Started |
| Channel strip component             | High     | 3 days   | Not Started |
| Fader component with touch support  | High     | 2 days   | Not Started |
| Meter visualization component       | High     | 2 days   | Not Started |
| Mute/Solo button group              | High     | 1 day    | Not Started |
| Pan/Knob control component          | Medium   | 1 day    | Not Started |
| Main mix view layout                | High     | 2 days   | Not Started |
| WebSocket state synchronization     | High     | 2 days   | Not Started |

### Phase 5: Advanced Features (Weeks 9-12)

**Goal:** Feature parity with basic mixing station functionality

| Task                        | Priority | Estimate | Status      |
| --------------------------- | -------- | -------- | ----------- |
| EQ editor component         | Medium   | 3 days   | Not Started |
| Compressor/Gate editor      | Medium   | 3 days   | Not Started |
| Aux/Bus send matrix         | Medium   | 2 days   | Not Started |
| DCA groups management       | Medium   | 2 days   | Not Started |
| Scene recall interface      | Medium   | 2 days   | Not Started |
| Channel configuration panel | Medium   | 2 days   | Not Started |

### Phase 6: Polish & Deployment (Weeks 12-14)

**Goal:** Production-ready application

| Task                           | Priority | Estimate | Status      |
| ------------------------------ | -------- | -------- | ----------- |
| Responsive design optimization | Medium   | 3 days   | Not Started |
| Performance optimization       | Medium   | 2 days   | Not Started |
| Docker deployment setup        | Medium   | 1 day    | Not Started |
| Documentation                  | Medium   | 2 days   | Not Started |
| End-to-end testing             | High     | 3 days   | Not Started |

---

## Feature Scope (MVP)

### Must Have (P0)

- [ ] Connect to single mixer via MIDI or OSC
- [ ] View and control channel faders (16-32 channels)
- [ ] Mute/unmute channels
- [ ] View meters in real-time
- [ ] Basic pan control
- [ ] Scene recall

### Should Have (P1)

- [ ] Multiple simultaneous mixer connections
- [ ] EQ control (parametric 4-band)
- [ ] Compressor/Gate control
- [ ] Aux sends matrix
- [ ] Channel naming/coloring
- [ ] DCA group assignment

### Nice to Have (P2)

- [ ] Custom layer layouts
- [ ] MIDI controller input (control surfaces)
- [ ] Touch gestures (pinch zoom, swipe)
- [ ] Multiple client sync
- [ ] Offline scene editing
- [ ] Plugin system for custom boards

---

## Technical Decisions

### Backend

- **Framework:** FastAPI (async, WebSocket native, OpenAPI docs)
- **State:** In-memory with optional Redis for multi-instance
- **Database:** SQLite for scenes/config, JSON files for portable configs
- **Protocol libs:** python-rtmidi (MIDI), python-osc (OSC)
- **Validation:** Pydantic v2

### Frontend

- **Framework:** Mithril.js (ultra-lightweight 10kb, fast auto-redraw)
- **State:** Meiosis pattern with Mithril streams
- **UI:** Custom components (no heavy UI library)
- **Styling:** TailwindCSS
- **Build:** Vite

### Communication

- **REST:** Configuration, scenes, device management
- **WebSocket:** Real-time parameters, meters, state sync

---

## Risk Assessment

| Risk                         | Likelihood | Impact | Mitigation                                |
| ---------------------------- | ---------- | ------ | ----------------------------------------- |
| Latency in real-time control | Medium     | High   | Optimize WebSocket, debounce updates      |
| Board protocol complexity    | High       | Medium | Start with well-documented boards         |
| State sync conflicts         | Medium     | Medium | Server authoritative, conflict resolution |
| Browser performance (meters) | Medium     | Low    | Canvas rendering, throttle updates        |

---

## Success Metrics

1. **Latency:** < 50ms round-trip for fader movements
2. **Reliability:** Zero lost commands during normal operation
3. **Compatibility:** Support 3+ major mixer brands
4. **Usability:** Intuitive enough for live use without training

---

## Next Steps (Immediate)

1. ✅ Create project roadmap (this document)
2. ✅ Define Pydantic models for unified mixer state
3. ✅ Create enhanced pluggy hookspec with state awareness
4. ✅ Design FastAPI endpoint schema
5. ✅ Migrate XAir board plugin to new architecture
6. ✅ Create frontend component specification (Mithril/Meiosis)
7. 🔲 Migrate Qu24 and GLD board plugins
8. 🔲 Wire up StateManager with actual board plugins
9. 🔲 Set up frontend project with Vite + Mithril.js
10. 🔲 Implement core UI components (Fader, Meter, ChannelStrip)

---

_Last Updated: December 20, 2025_
