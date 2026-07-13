# EchoCity — AI Civilization Runtime

A living, offline AI Civilization Operating System. EchoCity is **not** a chatbot simulation; it is a deterministic world engine run on a continuous background tick loop, enhanced by asynchronous local AI reasoning. 

As the **Higher Self**, you observe and subtly influence the cognitions and relationships of 8 citizens in real-time through the **EchoShell** dashboard, gathering evidence to accuse suspects and stage trials in the Court of EchoCity.

---

## Technical Constraints & Target Specs
*   **Completely Offline & Zero Cost**: Runs entirely on your local machine using no paid APIs.
*   **CPU-Only Inference**: Optimized for an Intel i5 CPU with 16–24 GB RAM using local Ollama models.
*   **OSI-Compliant License Target**: Configured for **SmolLM2 1.7B Instruct** (Apache-2.0).
*   **Database Persistence**: Uses a local SQLite database (`echocity.db`) via SQLAlchemy 2.0 ORM models to auto-save and recover simulation frames.
*   **Responsive Simulation**: A non-blocking background queue processes local AI reasoning tasks asynchronously under a strict concurrency cap (concurrency = 2) to protect CPU execution times.

---

## Quick Start Guide

### 1. Requirements & Dependencies
*   Python 3.12+ (managed with standard virtual environments or `uv`)
*   Node.js (for pnpm Next.js frontend compilation)
*   [Ollama](https://ollama.com/) (running locally)

### 2. Pull the Local Model
Start your local Ollama server, then pull the target model:
```bash
ollama pull smollm2:1.7b-instruct-q4_K_M
```

### 3. Backend Setup & Run
Configure python settings and start the FastAPI server:
```powershell
# Navigate to the backend directory
cd the-main-backend/backend

# Create virtual environment and install packages
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Start the FastAPI server (auto-seeds and sets up WebSocket endpoints)
.\venv\Scripts\python -m uvicorn app.main:app --reload
```
The server will boot up and bind to `http://localhost:8000`.

### 4. Frontend Setup & Run
Compile and launch the dashboard console:
```bash
# Navigate to frontend directory
cd echo-city-ai-os

# Install node dependencies
pnpm install

# Start Next.js development server (Webpack fallback enabled to prevent Turbopack panics)
pnpm dev
```
Open `http://localhost:3000` in your web browser.

---

## How to Play & CLI Controls

When you start the backend, the simulation initializes at **Day 1, 06:00 AM** with all 8 agents seeded with demographic data, schedule activities, and initial memories.

You interact with the city using the Terminal console located at the bottom of the Web UI:

### Turn-Based Controls (Pacing)
The simulation automatic tick loop advances every **30 seconds**. You can pause this loop and run the simulation in a turn-based pacing style using these commands:
*   `pause`: Halts the automatic background ticks.
*   `resume` (or `start`): Resumes the automatic background clock.
*   `tick`: Manually advances the simulation by exactly one minute (1 tick) and immediately persists the new state to the database.
*   `sim-save`: Force commits the active simulation frame to the SQLite database.
*   `sim-status`: Displays the current clock day, ticks, active scene step, and active agents list.

### Player Actions
*   `observe [location]`: View which agents are currently present at a location.
*   `question <agent_id>`: Query an agent's memories. The local AI generates character-authentic dialogue responses containing indexed memory summaries.
*   `collect <agent_id> <memory_index>`: Add an agent's memory to your evidence case file.
*   `suggest / warn / comfort / encourage <agent_id>`: Cast cognitive nudges to alter the agent's stress, suspicion, or needs, triggering background narrative generation tasks.
*   `court.exe`: Enters Court scene context.
*   `accuse <agent_id>`: Accuses a suspect agent using your collected case files, starting the trial engine to render a verdict.

---

## Verification & Testing

### Dynamic Persistence Check
Verify database seeding, Ollama connection, priority queuing, and SQLite saving/loading operations using the script:
```powershell
.\venv\Scripts\python scripts/verify_ai_persistence.py
```

### Unit Tests
Verify mock-mode fallback coverage:
```powershell
.\venv\Scripts\python -m pytest
```
*   **Result**: 173 / 173 test cases pass successfully.

---

## Database Configuration Settings
You can customize the model name or database location in the backend via environment variables or a `.env` file:
*   `OLLAMA_MODEL` (default: `smollm2:1.7b-instruct`)
*   `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
*   `DATABASE_URL` (default: `sqlite+aiosqlite:///./echocity.db`)
