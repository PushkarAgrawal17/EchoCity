# EchoCity

You are not a character in EchoCity — you're the invisible Higher Self,
watching the city's residents live their own lives through a bank of
floating instrument windows: a live thought stream, a relationship graph,
citizen dossiers, and a timeline of what's unfolding. You influence the
city by typing into **Synaptic Override**, EchoCity's terminal.

Built for the "On-device AI" hackathon track.

## Run it

```bash
npm install
npm run dev
```

Open the printed local URL (desktop browser, fullscreen recommended).

## Using EchoCity

Five windows float over the desktop. Drag any title bar to move it, click a
window to bring it to front, minimize with `–` (reopen from the dock at the
bottom of the screen):

- **Stream of Consciousness** — the live action log, plus decorative
  corrupted "memory fragments" underneath.
- **Synaptic Override** — the terminal. Type a command, `Enter` to run,
  `↑`/`↓` for history, `Tab` to autocomplete. Try `help`, `inspect marcus`,
  `comfort emma`, `observe bank`, `trace rumor`.
- **Citizen Profile** — opens automatically when you `inspect` someone (or
  click a node in the relationship graph). Dossier / Relationships /
  Inventory tabs, plus a stress gauge driven by their current emotion.
- **Relationship Graph** — every agent as a node, every relationship as an
  edge. Click a node to open that citizen's profile.
- **Temporal Loom** — a live branching timeline of event categories
  (crime, work, social, relationship, legal) as they accumulate.

The **Horizon** bar up top shows simulated runtime, an animated waveform,
the current `inspect` target, and observer status.

## Architecture

```
src/
  components/
    desktop/      DraggableWindow, DesktopBackground, Dock — the window manager
    horizon/       HorizonHeader, Waveform (canvas-animated)
    streamOfConsciousness/
    terminal/      SynapticOverrideWindow + its line/input subcomponents
    citizenProfile/
    relationshipGraph/
    temporalLoom/
    common/        PortraitAvatar, EmotionBadge, GlassPanel
  hooks/           useDraggable, useWorldClock, useEventFeed, useHoveredAgent
  pages/           CityPage (composition root)
  services/        agentService, worldService, terminalService, eventService
  store/           zustand: agentStore, worldStore, windowStore, terminalStore, eventStore
  types/           Agent, Building, TerminalLine, CityEvent, ...
  constants/       design tokens (COLORS, EMOTION_COLORS)
  data/            agents.ts, buildings.ts, commands.ts, events.ts, dialogue.ts, inventory.ts
  utils/           id, time, textScramble
```

**No component owns data.** Every store hydrates itself by calling a
service; every service returns a `Promise`. Components only ever read from
stores via hooks and dispatch store actions.

### Window manager

`windowStore` is the single source of truth for every panel's position,
size, z-index, and open/minimized state. `DraggableWindow` is the one
reusable chrome component (title bar, drag handling via `useDraggable`,
focus-to-front, minimize) that every panel wraps itself in — no panel
reimplements window behavior.

### EchoShell commands still drive real state

`terminalStore.applyEffect` translates a command's side-effect into store
updates: `comfort`/`question` change an agent's emotion and trigger a
reaction; `inspect` opens the Citizen Profile window; `trace rumor` pushes
a synthetic event into the Stream of Consciousness. Nothing terminal-shaped
leaks into the window components themselves.

### About the previous version

An earlier pass of this project rendered an actual pixel-art Phaser city
(tile map, buildings, walking NPC sprites). That's been fully replaced by
this desktop/window-panel UI to match the intended reference design — the
Phaser dependency has been removed and that code deleted rather than left
half-wired.

### Backend integration path

Every function in `services/*.ts` documents its own replacement plan. In short:

| Service | Mock today | Becomes |
|---|---|---|
| `agentService` | reads `data/agents.ts` | `GET/POST /api/agents` |
| `worldService` | reads `data/buildings.ts`, `data/world.ts` | `GET /api/world`, `GET /api/weather` |
| `terminalService` | switch statement over `data/commands.ts` | `POST /api/echoshell/execute` |
| `eventService` | random sample from `data/events.ts` | WebSocket subscription `/ws/events` |

Stores call services and never touch mock data directly, so this swap
happens entirely inside `services/`, with zero changes required in
`components/` or `store/`.

## Stack

React · TypeScript · Vite · Tailwind CSS v4 · Zustand · Framer Motion ·
React Icons · clsx
