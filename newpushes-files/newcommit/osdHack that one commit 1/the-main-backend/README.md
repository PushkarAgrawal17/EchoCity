# EchoCity

A living AI city simulation. Not a chatbot, not a visual game — an
always-running world of autonomous agents, occasionally observed and
nudged by a player through EchoShell.

## Status

Milestone 0 — Repository Bootstrap. Infrastructure only: configuration,
logging, and a minimal FastAPI app. No simulation, database, or AI yet.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
cd backend
cp .env.example .env
uv sync
```

## Run

```bash
uv run python -m app.main
```

Then visit `http://127.0.0.1:8000/health`.

## Test

```bash
uv run pytest
```

## Lint / format / type-check

```bash
uv run ruff check .
uv run black .
uv run mypy .
```

## Project layout

```
backend/
  app/
    api/          # REST/WebSocket endpoints (thin, no business logic)
    core/         # config, logging, DI, app factory
    simulation/   # World, Clock, Scheduler (Milestone 3)
    agents/       # Agent, AgentManager (Milestone 5)
    events/       # EventBus (Milestone 4)
    memory/       # MemoryManager (Milestone 5)
    database/     # SQLAlchemy models & repositories (Milestone 2)
    llm/          # Ollama client, prompt builder (Milestone 6)
    websocket/    # ConnectionManager (Milestone 8)
    workers/      # Background tasks
    services/     # Business orchestration
    models/       # Shared data models
    utils/        # Generic helpers
    main.py       # Entry point
  tests/
```

See `01_ARCHITECTURE.md` and `02_ROADMAP.md` in the project docs for the
full architecture and milestone plan.
