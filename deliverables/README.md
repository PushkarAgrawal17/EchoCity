# EchoCity — Setup, Execution & Quick Start Guide

This document contains step-by-step instructions for running the EchoCity AI simulation locally. It details system dependencies, installation procedures, run commands, sample inputs, and expected output structures.

---

## 1. Prerequisites & Dependencies

To run EchoCity fully on-device, your system must have the following tools installed:

### Required Software Runtime
*   **Operating System**: Windows (tested and validated)
*   **Python**: Version `3.12` or higher
*   **Node.js**: Version `18.0` or higher (for Vite compilation)
*   **Ollama**: Running locally ([Download Ollama](https://ollama.com/))

### Backend Dependencies (Python)
The backend is built as a PEP-621 compliant package (`pyproject.toml`) and requires:
*   `fastapi >= 0.115` (API Server)
*   `uvicorn[standard] >= 0.32` (ASGI Web Server)
*   `pydantic >= 2.9` & `pydantic-settings >= 2.6` (Config & Settings validation)
*   `sqlalchemy >= 2.0` (SQL ORM)
*   `aiosqlite >= 0.20` (Asynchronous SQLite database adapter)
*   `websockets >= 13.1` (Real-time narrative event stream)

### Frontend Dependencies (React SPA)
The frontend dashboard relies on:
*   `react ^19.2.7` & `react-dom ^19.2.7`
*   `vite ^8.1.1` (Fast asset bundle and dev server)
*   `tailwindcss ^4.3.2` & `@tailwindcss/postcss ^4.3.2` (Styling engine)
*   `framer-motion ^12.42.2` (Draggable panel transitions & layout animations)
*   `zustand ^5.0.14` (Global client-side state manager)
*   `react-icons ^5.7.0` & `lucide-react` (Dashboard icons)

---

## 2. Step-by-Step Installation

### Step A: Setup the Local AI Model (Ollama)
Start your local Ollama client and run the following command in your terminal to pull the optimized 1.7 Billion parameter model:
```bash
ollama pull smollm2:1.7b-instruct-q4_K_M
```
> [!TIP]
> The default model in `config.py` is `smollm2:1.7b-instruct`. If you want to use the 4-bit quantized version (recommended for low-memory CPU inference), configure your `.env` file with:
> `OLLAMA_MODEL=smollm2:1.7b-instruct-q4_K_M`

### Step B: Configure and Run the Backend
1. Open a terminal and navigate to the backend directory:
   ```powershell
   cd backend
   ```
2. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\activate
   ```
4. Install all dependencies:
   ```powershell
   pip install -e .
   ```
5. *(Optional)* Setup your environment variables by copying `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
6. Start the FastAPI server:
   ```powershell
   python -m uvicorn app.main:app --reload
   ```
   *Expected Backend Binding*: `http://127.0.0.1:8000`

### Step C: Configure and Run the Frontend
1. Open a second terminal window and navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   *Expected Frontend Binding*: `http://localhost:5173` (open in web browser)

---

## 3. Running Verification & Demos

### 1. Dynamic Simulation CLI Demo
To run the full tick lifecycle, FSM schedules, EventManager routing, MemoryEngine compression, and AI Router bypass logic in pure CLI, run:
```powershell
# In backend folder with activated venv:
python scripts/hackathon_simulation.py
```

### 2. SQLite Database & Persistence Verification
To verify database seeding, local database connections, and memory state serialization:
```powershell
# In backend folder with activated venv:
python scripts/verify_ai_persistence.py
```

### 3. Automated Test Suite
To run the complete suite of 194 unit tests covering every subsystem:
```powershell
# In backend folder with activated venv:
python -m pytest
```

---

## 4. Sample Inputs & Expected Outputs

### Case 1: Dynamic Simulation CLI Demo
* **Command**:
  ```powershell
  python scripts/hackathon_simulation.py
  ```
* **Expected Output Log**:
  ```text
  =================================================================
            TEMPORAL LOOM - AI CIVILIZATION RUNTIME ENGINE
                   HACKATHON SIMULATION DEMO
  =================================================================

  [Step 1] Initializing SQLite database schema & simulation components...
  SUCCESS: Loaded 8 FSM NPCs and registered Event Bus listeners.

  [Step 2] Advancing Clock to 08:00 (FSM Schedule Boundary)...
  SUCCESS: Sophia transitioned FSM state. Decoupled Event Published: TICK (task=Planning)
    -> Payload: Agent=Sophia Bennett, Job=Artist, Time=08:00, Scheduled=painting at studio

  [Step 3] Simulating social co-location & LLM Memory Compression...
  Processing completed gossip reasoning in BrainService...
  SUCCESS: Gossip processed. Cognitive Memory compressed and saved:
    -> Memory: 'Sophia Bennett gossiped about Liam being near the market looking for silk'
    -> Cognitive Slots: Emotion=neutral, Importance=0.6, Participants=['Sophia Bennett', 'Marcus Hale'], Location=Cafe, Tags=['gossip', 'market']

  [Step 4] Querying AI Router for Player Interrogation...
  Query: 'What is your job?' -> Requires LLM Cognition? False (Bypassed! Returns instantly with zero-cost)
  Query: 'Can you explain why Liam was searching for silk?' -> Requires LLM Cognition? True (Routed to Reasoning Queue!)

  [Step 5] Serializing state & cognitive memories to SQLite database (echocity.db)...
  SUCCESS: All relationships and structured memories committed to SQLite.

  =================================================================
            SIMULATION COMPLETED SUCCESSFULLY (100% GREEN)
  =================================================================
  ```

### Case 2: Synaptic Override Console Interrogation
* **Sample Console Input**:
  ```text
  question sophia_bennett "What is your job?"
  ```
* **Expected Output**:
  ```text
  [Router Bypass - Local DB Resolve]
  Sophia Bennett: I work as a painter and artist in EchoCity, maintaining my studio nearby.
  ```

* **Sample Console Input (Complex Query)**:
  ```text
  question sophia_bennett "Why were you at the Cafe at 08:00?"
  ```
* **Expected Output (Priority Queue -> Ollama Generated)**:
  ```json
  {
    "dialogue": "I went to the Cafe to grab a quick coffee and clear my head before setting up the easel. I like the morning light there."
  }
  ```
