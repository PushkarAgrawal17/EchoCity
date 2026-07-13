# EchoCity

**A living AI city where every citizen has a mind of their own — and one of them is hiding something.**

EchoCity is a text-driven detective experience built on top of an autonomous NPC simulation. AI-controlled citizens go about their lives in a small simulated town, form memories of what they witness, and gossip about it when they cross paths. Somewhere in that web of secondhand rumors and firsthand accounts is the truth about a crime — and it's the player's job to dig through the noise, question the citizens, collect evidence, and convince the court.

> Built for a hackathon. This README explains what exists today, how to run it, and where the seams are. For a deep, concept-by-concept walkthrough of how everything works (intended for teammates or future contributors), see [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md).

---

## Table of Contents

- [What EchoCity Is](#what-echocity-is)
- [Current Status](#current-status)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Backend](#backend-setup)
  - [Frontend](#frontend-setup)
- [Running Tests](#running-tests)
- [Core Concepts at a Glance](#core-concepts-at-a-glance)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## What EchoCity Is

Under the hood, EchoCity is a **tick-based simulation** (think: a tiny game engine) populated with autonomous agents. Every tick:

1. The simulation clock advances.
2. Any scheduled tasks that are due get run.
3. Agents update themselves.
4. Agents who happen to be in the same location get a chance to gossip — sharing a memory with each other.
5. A `TICK` event is broadcast to anyone listening.

One crime has been seeded into this world with a single ground-truth culprit. A handful of witnesses know pieces of the truth, and as agents talk to each other, that knowledge spreads (and dilutes) through the population. The player explores this world through a command-line-style shell (`observe`, `question`, `collect`, `accuse`, ...), builds a case file out of the memories they collect as evidence, and submits it to a `CourtEngine` that deterministically decides whether the case holds up.

On top of that simulation sits a dashboard-style frontend — a dark, cyberpunk "AI Civilization Observatory" UI with a world feed, a citizen relationship graph, chat panels, and an in-browser terminal for issuing commands.

## Current Status

Being upfront about this, since it matters for anyone picking up the project:

| Layer | Status |
|---|---|
| **Backend simulation core** (World, Clock, Scheduler, Agents, Events, Memory, Conversation/Gossip, Crime, Court, Investigation, Shell) | ✅ Implemented and unit-tested (21 test files) |
| **Backend HTTP API** | ⚠️ Only `GET /health` is currently exposed. The simulation logic above is fully built and tested in Python, but it is **not yet wired up to FastAPI routes** that the frontend can call. |
| **Frontend UI** | ✅ Fully built dashboard (setup screen, world feed, relationship graph, chat, terminal) |
| **Frontend ↔ Backend integration** | ⚠️ Not yet connected. The frontend currently runs entirely on **hardcoded sample data** and simulates terminal command output client-side; it does not yet call the backend API. |

In short: two solid, independently-working halves that are ready to be wired together. That wiring (exposing simulation endpoints + a WebSocket for live ticks, and pointing the frontend's terminal/data hooks at them) is the natural next milestone — see [Roadmap](#roadmap).

## Tech Stack

**Backend**
- Python 3.12+
- [FastAPI](https://fastapi.tiangolo.com/) — HTTP API framework
- [Pydantic / pydantic-settings](https://docs.pydantic.dev/) — data validation & config management
- [SQLAlchemy](https://www.sqlalchemy.org/) + [Alembic](https://alembic.sqlalchemy.org/) + `aiosqlite` — database layer (scaffolded for a future persistence milestone)
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [uv](https://docs.astral.sh/uv/) — package/dependency manager
- `pytest`, `ruff`, `black`, `mypy` (strict mode) — testing & code quality

**Frontend**
- [Next.js 16](https://nextjs.org/) (App Router) + React 19 + TypeScript
- [Tailwind CSS v4](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/) primitives + [lucide-react](https://lucide.dev/) icons
- `pnpm` as the package manager

## Project Structure

```
EchoCity/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent, AgentManager, AgentState
│   │   ├── api/             # FastAPI routers (currently: /health)
│   │   ├── conversation/    # ConversationEngine, GossipEngine
│   │   ├── core/            # config, app factory, DI, logging
│   │   ├── court/           # CaseFile, Evidence, CourtEngine, Verdict
│   │   ├── crime/           # Crime, CrimeEngine, CrimeStatus
│   │   ├── events/          # Event, EventBus, EventType (pub/sub)
│   │   ├── investigation/   # InvestigationService (read-only queries)
│   │   ├── memory/          # Memory, MemoryManager, MemoryType
│   │   ├── shell/           # Command, Parser, Shell (text command interface)
│   │   ├── simulation/      # World, Clock, Scheduler, Location(Manager), SimulationEngine
│   │   └── main.py          # Entry point
│   ├── scripts/demo.py      # Runnable console demo of the whole simulation
│   ├── tests/                # 21 test files, one per subsystem
│   └── pyproject.toml
├── frontend/
│   ├── app/                 # Next.js App Router entry (layout, page, globals.css)
│   ├── components/          # TopBar, WorldFeed, RelationshipGraph, CognitiveGraph,
│   │                         # ChatSection, CommunicationCenter, EchoShell,
│   │                         # TerminalSection, WorldTimeline, SetupScreen, ui/
│   └── package.json
├── docs/
│   └── DOCUMENTATION.md     # Full concept-by-concept walkthrough
├── LICENSE
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed
- Node.js 18.18+ (Next.js 16 requirement) and [pnpm](https://pnpm.io/installation)

### Backend Setup

```bash
cd backend

# Install dependencies (creates a venv automatically)
uv sync

# Copy the example environment file and adjust if needed
cp .env.example .env

# Run the API server
uv run python -m app.main
```

The API will be live at `http://127.0.0.1:8000`. Confirm it's up:

```bash
curl http://127.0.0.1:8000/health
```

To see the simulation engine actually run end-to-end outside of the API (agents registered, ticks advancing, a scheduled task firing), run the console demo:

```bash
uv run python scripts/demo.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Start the dev server
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000). You'll land on a setup screen (identity + model/DB configuration — currently a mocked flow) before reaching the main dashboard, which renders with sample data.

## Running Tests

```bash
cd backend
uv run pytest
```

Static analysis / formatting:

```bash
uv run ruff check .
uv run black --check .
uv run mypy .
```

## Core Concepts at a Glance

A one-line summary of each backend subsystem — full detail lives in the documentation:

- **World** — the simulation root; owns every subsystem and drives the tick lifecycle.
- **Clock / Scheduler** — simulation time and "run this later" task scheduling, decoupled from wall-clock time.
- **Agent / AgentManager** — an NPC's state (location, goal, state) and the registry that owns them.
- **EventBus** — a synchronous pub/sub bus so subsystems can react to things (ticks, world start/stop, etc.) without being directly coupled.
- **Memory / MemoryManager** — what an individual agent knows, and how certain/how obtained (witnessed, heard, personal, evidence).
- **ConversationEngine / GossipEngine** — deterministic memory-sharing between two agents, and the logic that decides *when* co-located agents gossip.
- **CrimeEngine** — owns the one ground-truth crime and seeds the initial witness memories.
- **EvidenceManager / CaseFile / CourtEngine / Verdict** — the player's evidence-collection and case-submission pipeline, evaluated deterministically against the true culprit.
- **InvestigationService** — a read-only query layer the shell/frontend use to inspect agents and memories without being able to mutate simulation state.
- **Shell / Parser / Command** — parses player text input (`observe`, `question`, `collect`, `case`, `accuse`, `submit`, ...) into structured commands.

## Roadmap

- [ ] Expose simulation state (agents, locations, world feed, crime status) via FastAPI routes
- [ ] Add a WebSocket channel so the frontend can receive live tick/event updates instead of polling
- [ ] Wire the frontend's `EchoShell`/`TerminalSection` to call the real `Shell` command dispatcher instead of simulating responses client-side
- [ ] Replace sample data in `ChatSection`, `WorldFeed`, `RelationshipGraph`, and `CognitiveGraph` with live data from the backend
- [ ] Persist simulation state via the already-scaffolded SQLAlchemy/Alembic layer
- [ ] Real authentication (the current Google sign-in and Ollama/Qwen model connection flows in `SetupScreen` are mocked)

## Contributing

This started as a hackathon project, so the fastest way to get oriented is:

1. Read [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md) for the full architecture walkthrough.
2. Run `scripts/demo.py` to see the backend simulation working end-to-end in the console.
3. Run the test suite (`uv run pytest`) before and after making changes — every subsystem has its own test file.
4. Backend code follows strict `mypy` typing and `ruff`/`black` formatting; run those before committing.

## License

This project is licensed under the [MIT License](LICENSE).
