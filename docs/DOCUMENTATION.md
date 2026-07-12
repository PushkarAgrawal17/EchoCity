# EchoCity — Full Project Walkthrough

This document is meant to let someone with no prior context — a new teammate, a hackathon judge, or future-you six months from now — understand not just *what* EchoCity's code does, but *why* it's structured the way it is. It walks through every backend subsystem and every frontend piece, in the order you'd want to learn them in.

If you just want to run the project, see the root [`README.md`](../README.md). This file is the deep dive.

---

## 1. The Big Idea

EchoCity simulates a tiny town of AI-driven citizens. One of them has committed a crime. The rest of the town doesn't know the full truth — some saw it happen, some heard about it secondhand (and that version may already be less accurate), and most know nothing at all. As simulated time passes, citizens who happen to be in the same place talk, and knowledge (accurate or not) spreads.

The player's role is a detective: move around the town, observe citizens, question them about what they remember, and decide which of those "memories" are trustworthy enough to submit as evidence in court. The court doesn't take the player's word for it — it deterministically checks whether the submitted evidence actually points at the true culprit.

This is intentionally split into two independent halves:

- A **backend simulation** that is pure logic — no UI, no rendering, fully unit-testable — responsible for *the world, the agents, and the truth*.
- A **frontend dashboard** responsible for *presenting* that world to a player in an engaging way.

Right now these two halves exist and work on their own, but aren't connected yet (see [Current Status](../README.md#current-status) in the README). This doc explains both halves as they exist today.

---

## 2. Backend Architecture

### 2.1 Design philosophy

A few patterns repeat throughout the backend, and once you notice them, every module reads the same way:

- **Layered ownership, one direction of dependency.** Low-level subsystems (`Clock`) know nothing about the things built on top of them (`Scheduler`, `World`). A `Scheduler` only depends on `Clock`; it has never heard of `Agent` or `EventBus`. This is called out explicitly in nearly every module's docstring — e.g. Scheduler's docstring says outright that it has "no knowledge of World, SimulationEngine, Agents, Events, or AI."
- **Value objects are immutable.** `Location`, `Memory`, `Crime`, `Conversation`, `Evidence`, `Verdict`, and `Command` are all `@dataclass(frozen=True)`. They represent *facts* — a memory doesn't mutate, it gets replaced by a new memory (see `dataclasses.replace` usage in `MemoryManager.share_memory`).
- **Managers own collections; they don't contain business logic.** `AgentManager`, `MemoryManager`, `LocationManager`, `EvidenceManager` are all thin registries: register, get, remove, list. The *decisions* (when to gossip, how to evaluate a court case) live in dedicated `*Engine` classes that depend on the managers, not the other way around.
- **Engines make decisions; managers hold state.** This split — e.g. `GossipEngine` decides *when* two agents talk, `ConversationEngine` decides *how* a memory transfers, `MemoryManager` just stores the result — keeps each class small and independently testable.
- **Everything is constructor-injected.** `World` builds its own subsystems by default but accepts every one of them as an optional constructor argument. This is what makes the extensive test suite possible — tests construct a `World` with fake/minimal collaborators instead of the real ones.
- **Dependency injection via FastAPI's `Depends`**, not a custom DI container (see `app/core/dependencies.py`). `SettingsDep` is the first example; future subsystems (the `World` itself, once it's exposed via the API) will follow the same pattern.

### 2.2 The tick lifecycle (start here)

The single most important concept in the backend is the **tick**. Everything else exists to support it.

`World.tick()` is called once per simulation step and runs this sequence (`app/simulation/world.py`, `World.update()`):

1. **Clock.advance()** — increments the tick counter. Simulation time is always `tick_count * tick_duration_seconds` (default: 1 tick = 1 simulated minute) — never stored independently, so time and tick count can never drift apart.
2. **Scheduler.run_due_tasks()** — runs any one-shot or repeating task whose scheduled time has arrived.
3. **AgentManager.update_all()** — calls `.update()` on every registered agent (currently a placeholder; agents have no autonomous behavior yet — see [§2.4](#24-agents)).
4. **GossipEngine.process_tick(timestamp)** — agents who share a location may exchange one memory each (see [§2.6](#26-conversation--gossip)).
5. **EventBus.publish(TICK event)** — broadcasts that the tick happened, with the new tick count in the payload, so any subscriber (like the console demo's logger) can react.

`World` itself is only ever driven by two things:

- **Direct calls** — `world.start(); world.tick(); world.tick(); ...; world.stop()` — used by tests and `scripts/demo.py` for deterministic, instant execution.
- **`SimulationEngine`** (`app/simulation/simulation_engine.py`) — a thin real-time wrapper that just sleeps for `tick_interval` seconds and calls `world.tick()` in a loop. It contains *zero* simulation logic; its only job is pacing.

### 2.3 Clock & Scheduler

- **`Clock`** (`app/simulation/clock.py`): tracks `tick_count` and derives `current_time` from it. That's the entire class. It has no idea what a World or Agent is.
- **`Scheduler`** (`app/simulation/scheduler.py`): a min-heap of tasks keyed by `(run_at, insertion_order)`. `schedule_at(run_at, task, interval=None)` schedules a plain zero-argument callable. If `interval` is given, the task reschedules itself relative to its *previous* `run_at` (not "now") every time it fires — so a repeating task's cadence never drifts, even if `run_due_tasks()` is called late.

### 2.4 Agents

- **`AgentState`** (`app/agents/agent_state.py`): an enum — `IDLE`, `WALKING`, `WORKING`, `SLEEPING`, `TALKING`. Just the vocabulary; nothing decides *when* an agent changes state yet.
- **`Agent`** (`app/agents/agent.py`): a plain dataclass — `agent_id`, `name`, `state`, `goal` (free text, may be `None`), `location` (a `Location`, may be `None`). Deliberately "dumb" — no memory, relationships, emotions, schedule, or AI live on the `Agent` object itself; those are separate subsystems that reference an agent by ID instead of the class owning everything. `Agent.update()` currently does nothing — it's a documented placeholder for future decision logic.
- **`AgentManager`** (`app/agents/agent_manager.py`): register/remove/get/iterate over agents by ID. Registering a duplicate ID raises (a data-integrity bug worth surfacing loudly); removing an unknown ID just logs a warning and no-ops, because the caller's desired end state — "this agent is gone" — is already true.

### 2.5 Locations

- **`LocationType`** (`app/simulation/location_type.py`): the MVP world has exactly two location kinds, `CAFE` and `COURT`.
- **`Location`** (`app/simulation/location.py`): an immutable `id` / `name` / `type` triple.
- **`LocationManager`** (`app/simulation/location_manager.py`): register-and-lookup registry, same pattern as `AgentManager`.

### 2.6 Events (EventBus)

- **`EventType`** (`app/events/event_type.py`): currently `WORLD_STARTED`, `WORLD_STOPPED`, `TICK`, `AGENT_REGISTERED`, `AGENT_REMOVED`. Only events actually produced today — new gameplay events get added by whichever milestone introduces them, rather than being speculatively pre-declared.
- **`Event`** (`app/events/event.py`): immutable — `event_type`, `timestamp` (simulation time, supplied by the caller — never auto-derived from the wall clock, to keep the simulation's notion of time self-contained), `payload` (a free-form dict), and an auto-generated `event_id`.
- **`EventBus`** (`app/events/event_bus.py`): a synchronous publish/subscribe dispatcher. `subscribe(event_type, callback)` registers a listener; `publish(event)` calls every subscriber for that event's type, in registration order, on the same thread. No async, no queues, no persistence — deliberately the simplest thing that could work. This is how `scripts/demo.py` prints a line every tick without `World` needing to know anything about printing.

### 2.7 Memory

This is the mechanism that makes the whole detective premise work.

- **`MemoryType`** (`app/memory/memory_type.py`): classifies *how* a memory was obtained —`WITNESS` (agent directly saw it), `HEARD` (told to them by another agent — gossip), `PERSONAL` (about the agent's own experience), `EVIDENCE` (formally significant to the case).
- **`Memory`** (`app/memory/memory.py`): immutable — `id`, `summary`, `type`, `source` (an agent_id, or `"self"`), `timestamp`, `confidence` (0.0–1.0), `shared` (bool), and `subject_id` (who/what the memory is *about* — this is what `CourtEngine` checks against the real culprit).
- **`MemoryManager`** (`app/memory/memory_manager.py`): stores memories per agent (`dict[agent_id, list[Memory]]`). Because `Memory` is frozen, "marking a memory as shared" doesn't mutate it — `share_memory()` uses `dataclasses.replace()` to swap in a new copy with `shared=True` at the same list index.

### 2.8 Conversation & Gossip

Two collaborating classes with a clean separation of concerns: **when** vs. **how**.

- **`ConversationEngine`** (`app/conversation/conversation_engine.py`) — the "how." `share_memory(speaker_id, listener_id, memory_id)` copies one of the speaker's memories to the listener (with `source` rewritten to the speaker's ID, so a chain of gossip is traceable), marks the speaker's original as `shared`, and is a no-op if the listener already has that memory (no duplication). It never touches `Agent` objects directly — everything flows through `MemoryManager`.
- **`GossipEngine`** (`app/conversation/gossip_engine.py`) — the "when." Every tick, it groups currently-registered agents by their location, pairs up agents who share a location, and lets each pick one memory to offer to the other via `ConversationEngine`. It never transfers memory data itself — that's entirely delegated.

This is the mechanism by which a crime witnessed by one agent (`agent_3` in the seeded scenario) can end up known, in some form, by agents who were nowhere near it — because they happened to sit at the same cafe table as someone who *was* there, or as someone who heard from someone who was there.

### 2.9 Crime

- **`CrimeStatus`** (`app/crime/crime_status.py`): `UNSOLVED` / `SOLVED`.
- **`Crime`** (`app/crime/crime.py`): immutable ground truth — `culprit_id`, `victim_id`, `location_id`, `timestamp`, `status`, plus a human-readable `title`/`description`. Deliberately "not known in full by any single agent" — the whole game is that no one character has this object; the player has to reconstruct it from fragments.
- **`CrimeEngine`** (`app/crime/crime_engine.py`): owns exactly one hardcoded MVP crime — *"Theft of the Silver Necklace"* at the Cafe, `agent_2` as culprit, `agent_1` as victim — and seeds initial witness/hearsay memories into `MemoryManager` for the designated witness (`agent_3`) and a second agent who starts out having already heard about it (`agent_4`). `create_crime()` is idempotent: calling it twice returns the same `Crime` instead of creating a second one.

### 2.10 Investigation

- **`InvestigationService`** (`app/investigation/investigation_service.py`) is a deliberately narrow, **read-only** query layer over `AgentManager` and `MemoryManager` — `get_agent`, `list_agents`, `get_agent_memories`. It has no dependency on `ConversationEngine`, `GossipEngine`, or `CrimeEngine`, and cannot mutate anything. This is the boundary the player-facing shell (and eventually the frontend) is meant to query through, so that "looking at the world" can never accidentally change it.

### 2.11 Court — evidence, case files, and the verdict

The player-facing "prove your case" pipeline, built from four small pieces:

- **`Evidence`** (`app/court/evidence.py`): a `Memory` the player has chosen to collect, wrapped with an `id` and `collected_at` timestamp.
- **`EvidenceManager`** (`app/court/evidence_manager.py`): the player's full pool of collected evidence, keyed by the underlying memory's ID so collecting the same memory twice is a no-op rather than a duplicate. Takes a `current_time` callable in its constructor (defaults to a constant `0.0` placeholder until the real `Clock` is wired in) — a small but deliberate seam for testability.
- **`CaseFile`** (`app/court/case_file.py`): the *subset* of collected evidence the player has chosen to actually submit — add, remove, list, clear. Separate from `EvidenceManager` on purpose: you can collect ten pieces of evidence and only submit the three you think matter.
- **`CourtEngine`** (`app/court/court_engine.py`): the deterministic judge. `evaluate(case_file)` counts how many submitted pieces of evidence have `memory.subject_id == crime.culprit_id` and requires at least 2 (`_REQUIRED_CORRECT_EVIDENCE`) to win. It never mutates the `Crime`, `CaseFile`, or any `Evidence` — pure function of its inputs.
- **`Verdict`** (`app/court/verdict.py`): the immutable result — `success`, the true `culprit_id` (revealed regardless of outcome), submitted vs. required evidence counts, and a human-readable `message`.

### 2.12 Shell — the player's command interface

- **`Command`** (`app/shell/command.py`): an immutable `name` + `arguments` tuple.
- **`Parser`** (`app/shell/parser.py`): turns a raw input line into a `Command`, validated against a table of known commands and their expected argument counts (`help`, `ls`, `cd`, `pwd`, `tree`, `observe`, `question`, `collect`, `case`, `remove`, `clear`, `accuse`, `submit`). Unknown commands or wrong argument counts raise `ParseError`.
- **`Shell`** (`app/shell/shell.py`): dispatches parsed commands. Navigation (`cd`, `pwd`, `ls`, `tree`) is purely presentational, walking a small virtual filesystem-like tree of locations (`_ROOT`). Only `observe` and `question` actually reach into the simulation, via `InvestigationService` — everything else in the shell operates on the court/evidence objects it was constructed with (`EvidenceManager`, `CaseFile`, `CourtEngine`).

This is the same command vocabulary you'll see echoed (currently as *simulated*, hardcoded responses) in the frontend's `EchoShell`/`TerminalSection` components — see [§3.6](#36-echoshell--terminalsection).

### 2.13 Core: config, app factory, DI, logging

- **`config.py`**: a single `Settings` (pydantic `BaseSettings`) object, resolved once from env vars → `.env` file → declared defaults, and cached via `@lru_cache` in `get_settings()`. No other module reads environment variables directly — everything goes through `Settings`, which is what makes it overridable in tests.
- **`app_factory.py`**: `create_app()` builds the `FastAPI` instance and registers routers; a `lifespan` context manager runs `setup_logging()` and logs startup/shutdown. Keeping this separate from `main.py` means the app object itself is importable and testable without actually starting a server.
- **`dependencies.py`**: FastAPI's built-in `Depends` mechanism is the DI approach — `SettingsDep = Annotated[Settings, Depends(get_settings)]` is the first (and so far only) shared dependency; the module's docstring explicitly earmarks it as the place future shared dependencies (a `World` instance, a database session, etc.) will be added.
- **`logging.py`**: configures the *root* logger once, at startup, with a consistent format (`timestamp | LEVEL | logger name | message`). Every other module gets its own logger via `logging.getLogger(__name__)`, so log lines are traceable to the subsystem that produced them.

### 2.14 What's actually wired into the HTTP API today

Only `GET /health` (`app/api/health.py`) is registered on the FastAPI app right now, returning `{"status": "ok", "app": ..., "environment": ...}`. Every subsystem described above (§2.2–§2.12) is fully implemented and unit-tested as plain Python, but there are **no routes yet** that let an HTTP client create a `World`, advance ticks, list agents, run shell commands, or submit a case file. `scripts/demo.py` is currently the only way to see the full simulation run, and it does so by importing and driving the classes directly in a Python process — not over HTTP.

### 2.15 Testing

`backend/tests/` has one test file per subsystem (21 in total — e.g. `test_clock.py`, `test_scheduler.py`, `test_gossip_engine.py`, `test_court_engine.py`, `test_world_integration.py`), run with `pytest` (`asyncio_mode = "auto"` is set for any async tests). The layered, dependency-injected design described in §2.1 is what makes this possible — most classes can be tested with plain fakes instead of a running server or database. `test_world_integration.py` specifically exercises the tick lifecycle end-to-end rather than any single subsystem in isolation.

---

## 3. Frontend Architecture

### 3.1 Stack & conventions

Next.js 16 (App Router) + React 19 + TypeScript, styled with Tailwind CSS v4 and a handful of `shadcn/ui` primitives (see `components/ui/button.tsx`), icons from `lucide-react`. Every interactive component is a client component (`'use client'` at the top of the file) — there's currently no server-rendered data fetching; all data is local component state or hardcoded sample arrays.

### 3.2 Entry point: `app/page.tsx`

The root page manages exactly one piece of top-level state: `isSetupComplete`. It reads `localStorage.getItem('echocity_setup_complete')` on mount (guarded by an `isMounted` flag to avoid a hydration mismatch between server and client render) and shows `SetupScreen` until that's true, then renders the main three-column dashboard layout:

- **Column 1 (`ChatSection`)** — citizen chats + global chat, ~20% width.
- **Column 2 (center stack)** — `WorldFeed` on top, terminal below.
- **Column 3 (`RelationshipGraph`)** — citizen network + inspector panel.

`TopBar` sits above all three, with a `onResetSetup` callback that flips `isSetupComplete` back to `false`.

### 3.3 SetupScreen

A pre-dashboard onboarding flow with two identity modes (`local` — username/PIN, or a `google` sign-in), plus fields for connecting to a local LLM backend (Ollama or Qwen — URL + model name) and a Postgres database URL. **All of this is currently mocked**: `handleGoogleSignIn` and the "test connection" handlers (`testingOllama`, `testingQwen`, `testingDb`) simulate success after a `setTimeout` rather than making real network calls. This is the natural place to plug in real auth and real connection checks once there's a backend endpoint to hit.

### 3.4 Dashboard components

- **`TopBar`** — logo, current in-world day/time display, a citizen/location search bar, connection status indicators, and a profile dropdown.
- **`ChatSection`** — two tabs: "Citizen Chats" (a feed of conversations between AI agents — participants, location, timestamp, an emotion tag) and "Global Chat" (a simple send/receive message list). Currently backed by a `SAMPLE_MESSAGES` array.
- **`WorldFeed`** — the main narrative output, styled like a text-based novel: expandable event cards, color-coded by event type (`social`, `crime`, `weather`, `court`, `discovery`), each with a timestamp/location header and participant badges.
- **`RelationshipGraph`** / **`CognitiveGraph`** — a grid of citizen nodes (stress-level bars, click-to-select, emotion-based coloring) plus an expandable inspector panel showing a selected citizen's basic info, trust levels with other citizens, inventory, recent activity, and unlocked secrets. Backed by a hardcoded `CITIZENS` array with fields like `emotion`, `stress`, `trust`, `goal`, `secrets`.
- **`CommunicationCenter`** — an alternate/supporting messaging view, also driven by sample `Message` data with emotion tags.
- **`WorldTimeline`** — a chronological list of world events (`conversation`, `crime`, `relationship`, `system`, `world` types), each with a time, description, and icon.

### 3.5 EchoShell / TerminalSection

An in-browser terminal styled after a real shell (monospace font, cyan prompt, command history navigable with arrow keys, tab-autocomplete). It recognizes the same command vocabulary as the backend `Shell` — `observe`, `inspect`, `cat`, `trace`, `tail`, `suggest`, `question`, `watch` — but today, `handleCommand` builds a **simulated response string locally** (e.g. hand-written text like `"{citizen}: Currently at Bank, Stress: 65%, Trust: 42%"`) rather than sending the command to the backend's `Parser`/`Shell` and rendering a real result. This is the single most direct integration point between the two halves of the project once the API is exposed — see the [Roadmap](../README.md#roadmap).

### 3.6 Styling system

`app/globals.css` defines the theme as CSS custom properties — a dark cyberpunk palette (background `#0B0F14`, cyan accents `#00D9FF`/`#6EE7FF`, semantic colors for success/warning/destructive states), consumed throughout via Tailwind utility classes rather than inline styles. Typography pairs a standard sans body font with a monospace font for anything terminal- or code-flavored. The visual language leans on glassmorphism (backdrop blur, translucent panel backgrounds), generous whitespace, and subtle hover/glow transitions — deliberately spacious rather than dense.

### 3.7 Data shapes currently in use

These aren't formal shared types yet (frontend and backend define their own shapes independently, since they aren't connected), but they're the informal contracts each component expects:

```typescript
// Citizen (RelationshipGraph / CognitiveGraph)
{
  id: string
  name: string
  occupation: string      // or `role` in some components
  emotion: string
  stress: number           // 0–100
  trust: number | Record<string, number>
  location: string
  goal: string
  secrets?: string[]
}

// World/Timeline Event
{
  id: string
  day: number
  time: string
  location: string
  type: 'social' | 'crime' | 'weather' | 'court' | 'discovery'
  participants?: string[]
  narrative: string
}

// Chat Message
{
  id: string
  speaker: string
  content: string
  location: string
  emotion: 'happy' | 'neutral' | 'sad' | 'angry' | 'curious' | 'concerned' | 'determined'
  timestamp: string
}
```

Whoever wires up the real API integration will want to reconcile these against the backend's actual dataclasses (`Agent`, `Memory`, `Crime`, `Verdict`, etc.) — they overlap conceptually but aren't identical today.

---

## 4. How the Two Halves Are Meant to Fit Together

Tracing the intended (not-yet-built) data flow helps make sense of why each backend piece exists:

1. A `World` runs (via `SimulationEngine` or a background task started by the FastAPI `lifespan`), ticking forward and publishing `EventBus` events.
2. New FastAPI routes would expose read access through `InvestigationService` (list agents, get an agent's memories) and mutation access through the `Shell` (parse and execute a command) and `Court` pipeline (collect evidence, build a case file, submit for a verdict).
3. A WebSocket (or polling endpoint) would let the frontend subscribe to `TICK`/`AGENT_REGISTERED`/etc. events from the `EventBus` and turn them into `WorldFeed`/`WorldTimeline` entries instead of hardcoded sample events.
4. `EchoShell`'s `handleCommand` would `POST` the raw command string to a `/shell` endpoint (or similar) and render the backend `Shell`'s actual response instead of a simulated one.
5. `SetupScreen`'s connection tests would hit real health-check endpoints for whichever LLM backend and database the player configures.

None of this wiring exists yet — this section is a map for whoever builds it next, grounded in what each existing piece already does.

---

## 5. Glossary

| Term | Meaning |
|---|---|
| **Tick** | One discrete step of simulation time; the fundamental unit `World.tick()` advances by. |
| **World** | The root object owning every simulation subsystem and the tick lifecycle. |
| **Agent** | An NPC's simulation state (not its AI/behavior — currently a placeholder). |
| **Memory** | A single fact an agent knows, with a type (witnessed/heard/personal/evidence), confidence, and source. |
| **Gossip** | The automatic, deterministic sharing of one memory between two co-located agents on a tick. |
| **Crime** | The single ground-truth incident seeded into the world, with a hidden culprit. |
| **Evidence** | A memory the player has chosen to collect for the case. |
| **Case File** | The subset of collected evidence the player actually submits to court. |
| **Verdict** | The deterministic result of evaluating a case file against the true crime. |
| **EventBus** | The synchronous pub/sub mechanism subsystems use to broadcast what happened. |
| **Shell** | The parsed-command interface the player uses to interact with the simulation. |
