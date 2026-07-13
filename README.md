# EchoCity — AI Civilization Runtime

EchoCity is a living, offline AI Civilization Operating System. It runs a deterministic world engine driven by a continuous background tick loop, enhanced by decoupled, asynchronous local AI reasoning.

As the **Higher Self**, you observe and subtly influence the cognitions and relationships of 8 simulation agents in real-time through the interactive dashboard, collecting evidence to accuse suspects and stage trials in the Court of EchoCity.

---

## Key Subsystem Architectures

### 1. NPC Manager (FSM)
* **Deterministic FSM Engine**: NPCs are modeled as deterministic finite state machines. Each agent tracks cognitive needs (energy, confidence, suspicion), directional relationships (trust, friendship, fear), stress levels, daily schedule routines, inventories, goals, memories, locations, and active tasks.
* **Decoupled reasoning**: The NPC Manager never talks to the LLM directly. When a transition occurs that requires cognitive evaluation (e.g. schedule boundaries, high-stress bank opportunities, or co-located dialogue chances), it publishes the corresponding event to the EventBus.

### 2. Event Manager
* **Interception & Routing**: Routes simulation events. If an event requires cognitive reasoning, it automatically enqueues the task on the `ReasoningQueue` (with custom priority weights: e.g. `WITNESS_FOUND` at priority `0` for immediate processing). Otherwise, it executes synchronous state updates immediately via registered handlers.

### 3. Memory Engine
* **Cognitive Slot Storage**: Processes raw events into structured memories storing: summary, emotion, importance, participants, location, timestamp, and tags.
* **Latency Optimization (Rule Bypass)**: Simple, routine events (e.g. going to bed, walking) bypass the LLM and generate rule-based memories immediately to protect CPU cycles. Complex events (e.g. dialogue, crime, social interactions) are run through the `event_compression` LLM reasoning task.

### 4. Context Builder
* **Token Minimization**: Formats and minimizes prompt contexts dynamically to fit within tight CPU context windows. Condenses agent traits, formats Big Five scales (e.g., `O:80, C:50`), maps co-located relationships into compact string lists, and caps memories to the top 1-3 most relevant items.

### 5. Low-Latency Prompt Templates
* **JSON mode**: All LLM prompt templates are optimized to return strict raw JSON payloads.
* **CPU Optimized**: Prompts are kept short and direct, ensuring the combined context is typically under **200 tokens** to maximize local CPU token-generation speeds.

---

## Repository Structure

*   `/backend` - FastAPI server, SQLite persistence (SQLAlchemy 2.0 ORM), local Ollama client, reasoning queue, and the 185-test suite.
*   `/frontend` - Next.js interactive UI dashboard console compiled using Next.js dev server.
*   `EchoCity_NPC_Bible.md` - Core demographic, relationship, and narrative guidelines for all 8 simulation characters.

---

## Quick Start Guide

### 1. Requirements
*   Python 3.12+ (managed with standard virtual environments or `uv`)
*   Node.js (for Next.js frontend compilation)
*   [Ollama](https://ollama.com/) (running locally)

### 2. Pull the target model
Start your local Ollama instance, then pull the target model:
```bash
ollama pull smollm2:1.7b-instruct
```

### 3. Backend Setup & Run
Configure Python settings and start the FastAPI server:
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment and install packages
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Start the FastAPI server (auto-seeds and registers WebSocket endpoints)
.\venv\Scripts\python -m uvicorn app.main:app --reload
```
The server will boot up and bind to `http://127.0.0.1:8000`.

### 4. Frontend Setup & Run
Compile and launch the dashboard console:
```bash
# Navigate to frontend directory
cd frontend

# Install node dependencies
pnpm install

# Start Next.js development server
pnpm dev
```
Open `http://localhost:3000` in your web browser.

---

## Verification & Testing

### Dynamic Persistence Check
Verify database seeding, Ollama connection, priority queuing, and SQLite saving/loading operations using the script:
```powershell
.\venv\Scripts\python scripts/verify_ai_persistence.py
```

### Unit Tests
Verify all mock-mode fallback and architecture coverages:
```powershell
.\venv\Scripts\python -m pytest
```
*   **Result**: 185 / 185 test cases pass successfully.

---

## Configuration Settings
You can customize the model name or database location in the backend via environment variables or a `.env` file:
*   `OLLAMA_MODEL` (default: `smollm2:1.7b-instruct`)
*   `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
*   `DATABASE_URL` (default: `sqlite+aiosqlite:///./echocity.db`)
