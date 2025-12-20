# Ludwig Frontend Specification

## Overview

The Ludwig frontend is a web-based audio mixer control interface designed to provide remote control of various mixing consoles. The interface should be responsive, touch-friendly, and provide real-time feedback with minimal latency.

---

## Technology Stack

| Component | Recommendation      | Rationale                                                |
| --------- | ------------------- | -------------------------------------------------------- |
| Framework | **Mithril.js**      | Ultra-lightweight (10kb), fast, simple API, auto-redraw  |
| State     | **Meiosis pattern** | Functional state management with streams, no boilerplate |
| Streams   | Mithril Stream      | Built-in reactive streams for state updates              |
| Styling   | TailwindCSS         | Utility-first, responsive, dark mode support             |
| WebSocket | Native WebSocket    | No library needed, reconnection logic only               |
| Build     | Vite                | Fast dev server, optimized builds                        |
| Canvas    | HTML5 Canvas        | For meters (performance)                                 |

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

```javascript
// components/Fader.js
import m from 'mithril'

export const Fader = {
  oninit(vnode) {
    this.dragging = false
    this.startY = 0
    this.startValue = 0
  },

  onPointerDown(e, vnode) {
    this.dragging = true
    this.startY = e.clientY
    this.startValue = vnode.attrs.value
    e.target.setPointerCapture(e.pointerId)
  },

  onPointerMove(e, vnode) {
    if (!this.dragging) return
    const delta = (this.startY - e.clientY) / 200 // 200px = full range
    const newValue = Math.max(0, Math.min(1, this.startValue + delta))
    vnode.attrs.onChange(newValue)
  },

  onPointerUp(e) {
    this.dragging = false
  },

  onDblClick(vnode) {
    // Double-tap resets to 0dB (0.75 normalized)
    vnode.attrs.onChange(0.75)
  },

  view(vnode) {
    const { value, disabled, color = '#3b82f6', showValue = true } = vnode.attrs
    const percentage = value * 100

    return m(
      '.fader.relative.h-48.w-8.bg-gray-800.rounded',
      {
        class: disabled ? 'opacity-50' : 'cursor-ns-resize',
        onpointerdown: e => this.onPointerDown(e, vnode),
        onpointermove: e => this.onPointerMove(e, vnode),
        onpointerup: e => this.onPointerUp(e),
        ondblclick: () => this.onDblClick(vnode),
      },
      [
        // Track
        m('.absolute.bottom-0.left-1.right-1.bg-gray-600.rounded', {
          style: { height: '100%' },
        }),
        // Fill
        m('.absolute.bottom-0.left-1.right-1.rounded.transition-all', {
          style: { height: `${percentage}%`, backgroundColor: color },
        }),
        // Handle
        m(
          '.absolute.left-0.right-0.h-4.bg-white.rounded.shadow-lg.cursor-grab',
          {
            style: { bottom: `calc(${percentage}% - 8px)` },
          }
        ),
        // Value label
        showValue &&
          m(
            '.absolute.-right-8.text-xs.text-gray-400',
            {
              style: { bottom: `calc(${percentage}% - 6px)` },
            },
            `${Math.round(value * 100)}%`
          ),
      ]
    )
  },
}
```

Features:

- Touch drag with pointer events
- Double-tap to reset to 0dB
- Value tooltip while dragging
- Optional dB scale markers

### Meter Component

```javascript
// components/Meter.js
import m from 'mithril'

export const Meter = {
  oncreate(vnode) {
    this.canvas = vnode.dom
    this.ctx = this.canvas.getContext('2d')
    this.peakHold = 0
    this.peakTimer = 0
    this.animate(vnode)
  },

  animate(vnode) {
    const { level = 0, peak } = vnode.attrs
    const { width, height } = this.canvas

    // Clear
    this.ctx.fillStyle = '#1f2937'
    this.ctx.fillRect(0, 0, width, height)

    // Calculate fill height
    const fillHeight = level * height

    // Gradient fill
    const gradient = this.ctx.createLinearGradient(0, height, 0, 0)
    gradient.addColorStop(0, '#22c55e') // Green
    gradient.addColorStop(0.7, '#eab308') // Yellow at -6dB
    gradient.addColorStop(0.9, '#ef4444') // Red at -3dB

    this.ctx.fillStyle = gradient
    this.ctx.fillRect(0, height - fillHeight, width, fillHeight)

    // Peak hold
    if (peak !== undefined) {
      this.ctx.fillStyle = '#ffffff'
      const peakY = height - peak * height
      this.ctx.fillRect(0, peakY, width, 2)
    }

    requestAnimationFrame(() => this.animate(vnode))
  },

  view(vnode) {
    const { orientation = 'vertical', width = 12, height = 150 } = vnode.attrs

    return m('canvas.rounded', {
      width: orientation === 'vertical' ? width : height,
      height: orientation === 'vertical' ? height : width,
    })
  },
}
```

Features:

- Canvas-rendered for performance
- Configurable peak hold time
- Gradient display (green → yellow → red)
- Smooth animation (requestAnimationFrame)

### Knob Component

```javascript
// components/Knob.js
import m from 'mithril'

export const Knob = {
  oninit() {
    this.dragging = false
    this.startY = 0
    this.startValue = 0
  },

  view(vnode) {
    const { value, min = 0, max = 1, detent, label, size = 'md' } = vnode.attrs
    const normalized = (value - min) / (max - min)
    const rotation = -135 + normalized * 270 // -135° to +135°

    const sizes = { sm: 'w-8 h-8', md: 'w-12 h-12', lg: 'w-16 h-16' }

    return m('.knob.flex.flex-col.items-center', [
      m(
        `.relative.${sizes[size]}.rounded-full.bg-gray-700.cursor-pointer`,
        {
          onpointerdown: e => {
            this.dragging = true
            this.startY = e.clientY
            this.startValue = value
            e.target.setPointerCapture(e.pointerId)
          },
          onpointermove: e => {
            if (!this.dragging) return
            const delta = (this.startY - e.clientY) / 100
            const range = max - min
            const newValue = Math.max(
              min,
              Math.min(max, this.startValue + delta * range)
            )
            // Snap to detent if close
            if (
              detent !== undefined &&
              Math.abs(newValue - detent) < range * 0.05
            ) {
              vnode.attrs.onChange(detent)
            } else {
              vnode.attrs.onChange(newValue)
            }
          },
          onpointerup: () => {
            this.dragging = false
          },
        },
        [
          // Indicator line
          m(
            '.absolute.top-1.left-1/2.w-0.5.h-3.bg-white.rounded.origin-bottom',
            {
              style: { transform: `translateX(-50%) rotate(${rotation}deg)` },
            }
          ),
          // Center dot
          m('.absolute.top-1/2.left-1/2.w-2.h-2.bg-gray-500.rounded-full', {
            style: { transform: 'translate(-50%, -50%)' },
          }),
        ]
      ),
      label && m('.text-xs.text-gray-400.mt-1', label),
    ])
  },
}
```

Features:

- Circular drag gesture
- Optional center detent (for pan)
- Value display on hover/drag

### Button Component

```javascript
// components/ToggleButton.js
import m from 'mithril'

const colorMap = {
  red: { active: 'bg-red-600', inactive: 'bg-gray-700 hover:bg-gray-600' },
  yellow: {
    active: 'bg-yellow-500 text-black',
    inactive: 'bg-gray-700 hover:bg-gray-600',
  },
  green: { active: 'bg-green-600', inactive: 'bg-gray-700 hover:bg-gray-600' },
  blue: { active: 'bg-blue-600', inactive: 'bg-gray-700 hover:bg-gray-600' },
}

const sizeMap = {
  sm: 'px-2 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
  lg: 'px-4 py-2 text-base',
}

export const ToggleButton = {
  view(vnode) {
    const {
      active,
      onToggle,
      label,
      activeColor = 'blue',
      size = 'md',
    } = vnode.attrs
    const colors = colorMap[activeColor]

    return m(
      'button.rounded.font-medium.transition-colors',
      {
        class: `${sizeMap[size]} ${active ? colors.active : colors.inactive}`,
        onclick: onToggle,
      },
      label
    )
  },
}

// Specialized buttons
export const MuteButton = {
  view(vnode) {
    return m(ToggleButton, {
      ...vnode.attrs,
      label: 'M',
      activeColor: 'red',
    })
  },
}

export const SoloButton = {
  view(vnode) {
    return m(ToggleButton, {
      ...vnode.attrs,
      label: 'S',
      activeColor: 'yellow',
    })
  },
}
```

### Channel Strip Component

```javascript
// components/ChannelStrip.js
import m from 'mithril'
import { Fader } from './Fader'
import { Meter } from './Meter'
import { Knob } from './Knob'
import { MuteButton, SoloButton } from './ToggleButton'

export const ChannelStrip = {
  view(vnode) {
    const { channel, meterLevel, actions } = vnode.attrs
    const { id, name, fader, mute, solo, pan, color } = channel

    return m(
      '.channel-strip.flex.flex-col.items-center.p-2.bg-gray-900.rounded-lg.gap-2',
      {
        style: { borderTop: `3px solid ${color || '#3b82f6'}` },
      },
      [
        // Meter
        m(Meter, { level: meterLevel, orientation: 'vertical' }),

        // Pan knob
        m(Knob, {
          value: pan,
          min: -1,
          max: 1,
          detent: 0,
          size: 'sm',
          onChange: v => actions.setPan(id, v),
        }),

        // Mute/Solo buttons
        m('.flex.gap-1', [
          m(MuteButton, {
            active: mute,
            onToggle: () => actions.setMute(id, !mute),
          }),
          m(SoloButton, {
            active: solo,
            onToggle: () => actions.setSolo(id, !solo),
          }),
        ]),

        // Fader
        m(Fader, {
          value: fader,
          onChange: v => actions.setFader(id, v),
        }),

        // Channel name
        m('.text-xs.text-center.text-gray-300.truncate.w-full', name || id),
      ]
    )
  },
}
```

---

## State Management

### Meiosis Pattern Overview

The Meiosis pattern uses streams for state management with a simple, functional approach:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Actions   │────▶│   Update    │────▶│    State    │
│  (patches)  │     │  (reduce)   │     │  (stream)   │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │    View     │
                                        │  (Mithril)  │
                                        └─────────────┘
```

### State Stream Setup

```javascript
// state/index.js
import Stream from 'mithril/stream'

// Initial state
const initialState = {
  connected: false,
  device: null,
  channels: {},
  meters: {},
  ui: {
    selectedChannel: null,
    currentView: 'mixer',
  },
}

// Create update stream for patches
const update = Stream()

// Create state stream by scanning patches
const states = Stream.scan(
  (state, patch) => ({ ...state, ...patch }),
  initialState,
  update
)

export { states, update }
```

### Actions Module

```javascript
// state/actions.js
import m from 'mithril'

export const createActions = (update, ws) => ({
  // Connection
  setConnected: connected => update({ connected }),

  // Channel controls
  setFader: (channelId, level) => {
    // Optimistic update
    update(state => ({
      channels: {
        ...state.channels,
        [channelId]: { ...state.channels[channelId], fader: level },
      },
    }))
    // Send to server
    ws.send(
      JSON.stringify({ type: 'fader', channel_id: channelId, value: level })
    )
  },

  setMute: (channelId, muted) => {
    update(state => ({
      channels: {
        ...state.channels,
        [channelId]: { ...state.channels[channelId], mute: muted },
      },
    }))
    ws.send(
      JSON.stringify({ type: 'mute', channel_id: channelId, value: muted })
    )
  },

  setPan: (channelId, pan) => {
    update(state => ({
      channels: {
        ...state.channels,
        [channelId]: { ...state.channels[channelId], pan: pan },
      },
    }))
    ws.send(JSON.stringify({ type: 'pan', channel_id: channelId, value: pan }))
  },

  // Bulk state update (from server)
  setState: newState => update({ ...newState }),

  // Meter updates (high frequency, no WebSocket send)
  updateMeters: meters => {
    update({ meters })
    m.redraw() // Force redraw for meter animation
  },

  // UI actions
  selectChannel: channelId => update({ ui: { selectedChannel: channelId } }),
  setView: view => update({ ui: { currentView: view } }),
})
```

### WebSocket Integration

```javascript
// state/websocket.js
import m from 'mithril'

export const createWebSocket = (url, actions) => {
  let ws = null
  let reconnectTimer = null

  const connect = () => {
    ws = new WebSocket(url)

    ws.onopen = () => {
      actions.setConnected(true)
      m.redraw()
    }

    ws.onclose = () => {
      actions.setConnected(false)
      m.redraw()
      // Reconnect after 2 seconds
      reconnectTimer = setTimeout(connect, 2000)
    }

    ws.onmessage = event => {
      const msg = JSON.parse(event.data)
      handleMessage(msg, actions)
    }
  }

  const handleMessage = (msg, actions) => {
    switch (msg.type) {
      case 'state':
        actions.setState({
          device: msg.data.device,
          channels: msg.data.channels,
        })
        break
      case 'parameter':
        actions.setChannelParam(msg.channel_id, msg.parameter, msg.value)
        break
      case 'meters':
        actions.updateMeters(msg.levels)
        break
      case 'pong':
        // Keepalive response
        break
    }
    m.redraw()
  }

  const send = message => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(message)
    }
  }

  const disconnect = () => {
    clearTimeout(reconnectTimer)
    ws?.close()
  }

  return { connect, send, disconnect }
}
```

### App Bootstrap

```javascript
// app.js
import m from 'mithril'
import { states, update } from './state'
import { createActions } from './state/actions'
import { createWebSocket } from './state/websocket'
import { Layout } from './views/Layout'
import { MixerView } from './views/MixerView'
import { ChannelDetail } from './views/ChannelDetail'
import { SendMatrix } from './views/SendMatrix'
import { Scenes } from './views/Scenes'

// Initialize WebSocket and actions
const ws = createWebSocket('ws://localhost:8000/ws', null)
const actions = createActions(update, ws)

// Re-wire WebSocket with actions
ws.actions = actions
ws.connect()

// Subscribe to state changes for auto-redraw
states.map(() => m.redraw())

// Route components receive state and actions
const withState = Component => ({
  view: () => m(Component, { state: states(), actions }),
})

// Routes
m.route(document.body, '/', {
  '/': withState(MixerView),
  '/channel/:id': withState(ChannelDetail),
  '/sends': withState(SendMatrix),
  '/scenes': withState(Scenes),
})
```

---

## Performance Considerations

### Mithril Auto-Redraw

Mithril automatically redraws after event handlers, but for high-frequency updates:

```javascript
// Disable auto-redraw for meter updates to batch them
ws.onmessage = event => {
  const msg = JSON.parse(event.data)
  if (msg.type === 'meters') {
    // Update state without triggering redraw
    Object.assign(state.meters, msg.levels)
  } else {
    handleMessage(msg, actions)
    m.redraw()
  }
}

// Dedicated meter animation loop (decoupled from state)
const meterLoop = () => {
  // Canvas components read directly from state.meters
  requestAnimationFrame(meterLoop)
}
requestAnimationFrame(meterLoop)
```

### Meter Rendering

- Use dedicated Canvas element per meter
- Meters read from state but render independently via `requestAnimationFrame`
- Throttle incoming meter WebSocket messages to 20Hz max
- Use `oncreate` lifecycle for canvas initialization

### Fader Updates

```javascript
// Debounce outgoing WebSocket messages
let faderTimeout = null
const debouncedFader = (channelId, value) => {
  // Immediate local update
  update(state => ({
    channels: {
      ...state.channels,
      [channelId]: { ...state.channels[channelId], fader: value },
    },
  }))

  // Debounced network send
  clearTimeout(faderTimeout)
  faderTimeout = setTimeout(() => {
    ws.send(JSON.stringify({ type: 'fader', channel_id: channelId, value }))
  }, 16) // ~60fps max send rate
}
```

### Large Channel Counts

- Use `onbeforeupdate` to skip unchanged channel strips:
  ```javascript
  onbeforeupdate(vnode, old) {
    return vnode.attrs.channel !== old.attrs.channel
        || vnode.attrs.meterLevel !== old.attrs.meterLevel
  }
  ```
- Virtualize channel list for >32 channels using intersection observer
- Only render visible channels with `m.fragment`

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
│   ├── components/
│   │   ├── ChannelStrip.js
│   │   ├── Fader.js
│   │   ├── Meter.js
│   │   ├── Knob.js
│   │   ├── ToggleButton.js
│   │   ├── EQEditor.js
│   │   ├── CompressorEditor.js
│   │   └── SendMatrix.js
│   ├── state/
│   │   ├── index.js            # State stream setup
│   │   ├── actions.js          # Action creators
│   │   └── websocket.js        # WebSocket connection
│   ├── views/
│   │   ├── Layout.js           # App shell with nav
│   │   ├── MixerView.js        # Main channel strip view
│   │   ├── ChannelDetail.js    # Single channel detail
│   │   ├── SendMatrix.js       # Aux/bus send grid
│   │   ├── Scenes.js           # Scene management
│   │   └── Settings.js         # Connection settings
│   ├── utils/
│   │   ├── db-conversion.js    # dB <-> normalized helpers
│   │   └── gestures.js         # Touch gesture utilities
│   ├── app.js                  # Entry point, routes
│   └── app.css                 # Tailwind + custom styles
├── index.html
├── package.json
├── tailwind.config.js
└── vite.config.js
```

### Example View Component

```javascript
// views/MixerView.js
import m from 'mithril'
import { ChannelStrip } from '../components/ChannelStrip'

export const MixerView = {
  view(vnode) {
    const { state, actions } = vnode.attrs
    const inputChannels = Object.values(state.channels)
      .filter(ch => ch.channel_type === 'input')
      .sort((a, b) => a.index - b.index)

    return m('.mixer-view.flex.flex-col.h-screen.bg-gray-950', [
      // Header
      m('header.flex.items-center.justify-between.p-4.bg-gray-900', [
        m('h1.text-xl.font-bold.text-white', [
          'Ludwig',
          state.device &&
            m('span.text-gray-400.ml-2', `- ${state.device.name}`),
        ]),
        m('.flex.items-center.gap-2', [
          m('.w-2.h-2.rounded-full', {
            class: state.connected ? 'bg-green-500' : 'bg-red-500',
          }),
          m(
            'span.text-sm.text-gray-400',
            state.connected ? 'Connected' : 'Disconnected'
          ),
        ]),
      ]),

      // Channel strips (horizontal scroll)
      m('.flex-1.overflow-x-auto.p-4', [
        m(
          '.flex.gap-2.min-w-max',
          inputChannels.map(channel =>
            m(ChannelStrip, {
              key: channel.id,
              channel,
              meterLevel: state.meters[channel.id] || 0,
              actions,
            })
          )
        ),
      ]),
    ])
  },
}
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

_Last Updated: December 20, 2025_
