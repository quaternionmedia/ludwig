# Ludwig Frontend Specification

## Overview

The Ludwig frontend is a web-based audio mixer control interface designed to provide remote control of various mixing consoles. The interface should be responsive, touch-friendly, and provide real-time feedback with minimal latency.

---

## Technology Stack

| Component   | Recommendation          | Rationale                                              |
| ----------- | ----------------------- | ------------------------------------------------------ |
| Framework   | **Svelte/SvelteKit**    | Lightweight, excellent reactivity, minimal bundle size |
| Alternative | React + Zustand         | If team prefers React ecosystem                        |
| Styling     | TailwindCSS             | Utility-first, responsive, dark mode support           |
| State       | Svelte stores / Zustand | Simple, reactive state management                      |
| WebSocket   | Native WebSocket        | No library needed, reconnection logic only             |
| Build       | Vite                    | Fast dev server, optimized builds                      |
| Canvas      | HTML5 Canvas            | For meters (performance)                               |

---

## Design Principles

1. **Touch-first**: All controls must work well on tablets (primary use case)
2. **Low latency**: Visual feedback < 16ms, round-trip < 100ms
3. **Dark mode**: Default theme optimized for low-light environments
4. **Accessibility**: Keyboard navigation, screen reader labels
5. **Responsive**: Adapt from phone to large tablets to desktop

---

## Core Views

### 1. Channel Strip View (Main)

The primary mixing view showing channel strips in a horizontal scrollable layout.

```
┌────────────────────────────────────────────────────────────────────────┐
│  [Menu]  Ludwig - QU-24              [Scene ▼] [Layers ▼]  [Settings] │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │
│  │ ▓▓▓ │ │ ▓▓  │ │ ▓   │ │ ▓▓▓ │ │ ▓   │ │ ▓▓  │ │ ▓▓▓ │ │ ▓▓▓ │     │
│  │ ▓▓▓ │ │ ▓▓  │ │ ▓   │ │ ▓▓▓ │ │ ▓   │ │ ▓▓  │ │ ▓▓▓ │ │ ▓▓▓ │     │
│  │ ▓▓▓ │ │ ▓▓  │ │ ▓   │ │ ▓▓▓ │ │ ▓   │ │ ▓▓  │ │ ▓▓▓ │ │ ▓▓▓ │     │
│  │  ○  │ │  ○  │ │  ○  │ │  ○  │ │  ○  │ │  ○  │ │  ○  │ │  ○  │ Pan │
│  │     │ │     │ │     │ │     │ │     │ │     │ │     │ │     │     │
│  │ [M] │ │ [M] │ │ [M] │ │[M]* │ │ [M] │ │[M]* │ │ [M] │ │ [M] │ Mute│
│  │ [S] │ │ [S] │ │[S]* │ │ [S] │ │ [S] │ │ [S] │ │ [S] │ │ [S] │ Solo│
│  │     │ │     │ │     │ │     │ │     │ │     │ │     │ │     │     │
│  │ ┃▓▓ │ │ ┃▓  │ │ ┃   │ │ ┃▓▓ │ │ ┃   │ │ ┃▓  │ │ ┃▓▓ │ │ ┃▓▓ │Fader│
│  │ ┃▓▓ │ │ ┃▓  │ │ ┃   │ │ ┃▓▓ │ │ ┃   │ │ ┃▓  │ │ ┃▓▓ │ │ ┃▓▓ │     │
│  │ ┃▓▓ │ │ ┃▓  │ │ ┃   │ │ ┃▓▓ │ │ ┃   │ │ ┃▓  │ │ ┃▓▓ │ │ ┃▓▓ │     │
│  │     │ │     │ │     │ │     │ │     │ │     │ │     │ │     │     │
│  │ Vox │ │ Gtr │ │ Key │ │ Drm │ │ Bs  │ │ Aux │ │ FX1 │ │ Main│ Name│
│  │  1  │ │  2  │ │  3  │ │  4  │ │  5  │ │  6  │ │  7  │ │ LR  │     │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘     │
│                                                                        │
│  ◄ ═══════════════════════════════════════════════════════════════ ►  │
└────────────────────────────────────────────────────────────────────────┘
```

**Channel Strip Component:**

- Vertical meter (canvas-rendered, 20fps)
- Pan knob (rotary control)
- Mute button (toggleable, red when active)
- Solo button (toggleable, yellow when active)
- Fader (vertical slider, touch-draggable)
- Channel name label (tappable to edit)
- Color indicator (scribble strip style)

### 2. Channel Detail View

Expanded view for a single channel with full control access.

```
┌────────────────────────────────────────────────────────────────────────┐
│  [← Back]  Channel 1: Lead Vocal                            [Settings]│
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────────────────┬─────────────────────────────────┐│
│  │         EQUALIZER                │          DYNAMICS              ││
│  │  ┌────────────────────────────┐  │  ┌───────────────────────────┐ ││
│  │  │    ╱╲                      │  │  │  Compressor    [ON]       │ ││
│  │  │   ╱  ╲     ╱╲              │  │  │                           │ ││
│  │  │──╱────╲───╱──╲─────────────│  │  │  Threshold  ════●═══════  │ ││
│  │  │         ╲╱    ╲            │  │  │  Ratio      ══●═════════  │ ││
│  │  └────────────────────────────┘  │  │  Attack     ═════●══════  │ ││
│  │                                  │  │  Release    ════════●═══  │ ││
│  │  LF    LMF    HMF    HF   [ON]  │  │  Gain       ═══●═════════  │ ││
│  │  ○     ○      ○      ○          │  │                           │ ││
│  │ 100Hz 400Hz  2kHz   8kHz        │  │  GR: ▓▓▓▓▓░░░░░  -6dB     │ ││
│  │ +3dB  -2dB   +1dB   0dB         │  └───────────────────────────┘ ││
│  └──────────────────────────────────┴─────────────────────────────────┘│
│                                                                        │
│  ┌──────────────────────────────────┬─────────────────────────────────┐│
│  │         SENDS                    │        ROUTING                  ││
│  │                                  │                                 ││
│  │  Aux 1 [IEM]   ═══════●══════   │  Main Mix:    [✓]              ││
│  │  Aux 2 [Mon]   ════●═════════   │  DCA 1 (Vox): [✓]              ││
│  │  Aux 3         ═●════════════   │  DCA 2:       [ ]              ││
│  │  Aux 4         ══════════════   │  Mute Grp 1:  [ ]              ││
│  │  FX 1 [Verb]   ═════●════════   │                                 ││
│  │  FX 2 [Delay]  ════●═════════   │                                 ││
│  │                                  │                                 ││
│  └──────────────────────────────────┴─────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────┘
```

### 3. Send Matrix View

Grid view for aux/bus sends from all channels.

```
┌────────────────────────────────────────────────────────────────────────┐
│  [Menu]  Sends Matrix                                      [Settings] │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│         │ Ch1  Ch2  Ch3  Ch4  Ch5  Ch6  Ch7  Ch8  ...                 │
│  ───────┼─────────────────────────────────────────────                │
│  Aux 1  │ [▓▓] [▓ ] [  ] [▓▓] [▓ ] [▓▓] [  ] [▓ ]                    │
│  Aux 2  │ [▓ ] [▓▓] [▓ ] [  ] [▓▓] [▓ ] [▓ ] [  ]                    │
│  Aux 3  │ [  ] [  ] [▓▓] [▓ ] [  ] [  ] [▓▓] [▓▓]                    │
│  Aux 4  │ [▓▓] [▓ ] [▓ ] [▓▓] [▓ ] [▓ ] [▓ ] [▓ ]                    │
│  FX 1   │ [▓ ] [▓▓] [  ] [▓ ] [▓▓] [  ] [  ] [▓ ]                    │
│  FX 2   │ [  ] [▓ ] [▓ ] [  ] [▓ ] [▓▓] [▓ ] [  ]                    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 4. Scene Management View

List and recall scenes, with preview capability.

```
┌────────────────────────────────────────────────────────────────────────┐
│  [Menu]  Scenes                               [+ New]      [Settings] │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  Current: Scene 3 - Worship Set                                        │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ ★ 1. Soundcheck           Modified: Dec 18, 2025               │  │
│  │   2. Service Start        Modified: Dec 15, 2025               │  │
│  │   3. Worship Set         [ACTIVE]                              │  │
│  │   4. Message              Modified: Dec 15, 2025               │  │
│  │   5. Closing              Modified: Dec 15, 2025               │  │
│  │                                                                 │  │
│  │                                                                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  [Recall Selected]  [Store Current]  [Preview]  [Edit Name]           │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 5. Settings / Connection View

Device configuration and connection management.

---

## Component Library

### Fader Component

```typescript
interface FaderProps {
  value: number // 0.0 - 1.0
  onChange: (v: number) => void
  min?: number // dB label
  max?: number // dB label
  color?: string
  disabled?: boolean
  showValue?: boolean
}
```

Features:

- Touch drag with momentum
- Double-tap to reset to 0dB
- Value tooltip while dragging
- Optional dB scale markers

### Meter Component

```typescript
interface MeterProps {
  level: number // 0.0 - 1.0
  peak?: number // Peak hold
  orientation: 'vertical' | 'horizontal'
  segments?: number // LED segment count
  colors?: {
    normal: string
    warning: string // -6dB
    clip: string // 0dB
  }
}
```

Features:

- Canvas-rendered for performance
- Configurable peak hold time
- Gradient or segmented display
- Smooth animation (requestAnimationFrame)

### Knob Component

```typescript
interface KnobProps {
  value: number
  onChange: (v: number) => void
  min: number
  max: number
  detent?: number // Center detent value
  label?: string
  size?: 'sm' | 'md' | 'lg'
}
```

Features:

- Circular drag gesture
- Optional center detent (for pan)
- Value display on hover/drag

### Button Component

```typescript
interface ToggleButtonProps {
  active: boolean
  onToggle: () => void
  label: string
  activeColor?: 'red' | 'yellow' | 'green' | 'blue'
  size?: 'sm' | 'md' | 'lg'
}
```

---

## State Management

### WebSocket Store (Svelte)

```typescript
// stores/mixer.ts
import { writable, derived } from 'svelte/store'

interface MixerState {
  connected: boolean
  device: DeviceInfo | null
  channels: Record<string, Channel>
  meters: Record<string, number>
}

function createMixerStore() {
  const { subscribe, set, update } = writable<MixerState>({
    connected: false,
    device: null,
    channels: {},
    meters: {},
  })

  let ws: WebSocket | null = null

  return {
    subscribe,
    connect: (url: string) => {
      ws = new WebSocket(url)
      ws.onopen = () => update(s => ({ ...s, connected: true }))
      ws.onclose = () => update(s => ({ ...s, connected: false }))
      ws.onmessage = event => {
        const msg = JSON.parse(event.data)
        handleMessage(msg, update)
      }
    },
    setFader: (channelId: string, level: number) => {
      ws?.send(
        JSON.stringify({ type: 'fader', channel_id: channelId, value: level })
      )
      update(s => ({
        ...s,
        channels: {
          ...s.channels,
          [channelId]: { ...s.channels[channelId], fader: level },
        },
      }))
    },
    // ... other methods
  }
}

export const mixer = createMixerStore()
```

### Derived Stores

```typescript
// Derived store for just input channels
export const inputChannels = derived(mixer, $mixer =>
  Object.values($mixer.channels).filter(ch => ch.channel_type === 'input')
)

// Derived store for connection status
export const isConnected = derived(mixer, $mixer => $mixer.connected)
```

---

## Performance Considerations

### Meter Rendering

- Use dedicated Canvas element
- Batch meter updates (don't re-render for each channel)
- Use `requestAnimationFrame` for smooth 60fps rendering
- Throttle incoming meter WebSocket messages to 20Hz max

### Fader Updates

- Debounce outgoing WebSocket messages (10-20ms)
- Use optimistic updates (update UI immediately, send async)
- Batch multiple rapid changes

### Large Channel Counts

- Virtualize channel list for >32 channels
- Only render visible channels
- Use intersection observer for lazy loading

---

## Responsive Breakpoints

| Breakpoint       | Width       | Channels Visible | Notes                            |
| ---------------- | ----------- | ---------------- | -------------------------------- |
| Mobile           | <640px      | 4                | Compact strips, swipe navigation |
| Tablet Portrait  | 640-1024px  | 8                | Standard strips                  |
| Tablet Landscape | 1024-1280px | 12               | Full strips with meters          |
| Desktop          | >1280px     | 16+              | Extended view with sends         |

---

## Accessibility

- All controls keyboard accessible
- ARIA labels on buttons and sliders
- Focus indicators
- High contrast mode option
- Screen reader announcements for parameter changes

---

## File Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── ChannelStrip.svelte
│   │   │   ├── Fader.svelte
│   │   │   ├── Meter.svelte
│   │   │   ├── Knob.svelte
│   │   │   ├── MuteButton.svelte
│   │   │   ├── SoloButton.svelte
│   │   │   ├── EQEditor.svelte
│   │   │   ├── CompressorEditor.svelte
│   │   │   └── SendMatrix.svelte
│   │   ├── stores/
│   │   │   ├── mixer.ts
│   │   │   ├── ui.ts
│   │   │   └── settings.ts
│   │   └── utils/
│   │       ├── websocket.ts
│   │       ├── db-conversion.ts
│   │       └── gestures.ts
│   ├── routes/
│   │   ├── +page.svelte          # Main mixer view
│   │   ├── +layout.svelte        # App shell
│   │   ├── channel/
│   │   │   └── [id]/+page.svelte # Channel detail
│   │   ├── sends/+page.svelte    # Send matrix
│   │   ├── scenes/+page.svelte   # Scene management
│   │   └── settings/+page.svelte # Settings
│   ├── app.css
│   └── app.html
├── static/
├── package.json
├── svelte.config.js
├── tailwind.config.js
└── vite.config.js
```

---

## API Contract Summary

### WebSocket Messages (Client → Server)

```json
{"type": "fader", "channel_id": "input_1", "value": 0.75}
{"type": "mute", "channel_id": "input_1", "value": true}
{"type": "pan", "channel_id": "input_1", "value": -0.5}
{"type": "parameter", "channel_id": "input_1", "parameter": "eq.bands.0.gain", "value": 3.0}
{"type": "subscribe", "channels": ["input_1", "input_2"]}
{"type": "ping"}
```

### WebSocket Messages (Server → Client)

```json
{"type": "state", "data": {...full MixerState...}}
{"type": "parameter", "channel_id": "input_1", "parameter": "fader", "value": 0.75}
{"type": "meters", "levels": {"input_1": 0.5, "input_2": 0.3, ...}}
{"type": "pong"}
```

---

_Last Updated: December 18, 2025_
