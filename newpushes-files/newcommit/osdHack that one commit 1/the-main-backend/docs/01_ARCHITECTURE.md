# EchoCity Architecture

Version: 2.0

---

# Purpose

This document defines the high-level architecture of EchoCity.

EchoCity is an offline cognitive social simulation.

The backend is responsible for simulating a believable world that exists independently of the player.

The player interacts only through EchoShell.

---

# High-Level Architecture

                     EchoShell
                         │
                         ▼
             Investigation Service
                         │
                         ▼
                     World
      ┌──────────────────────────────────────┐
      │              Simulation              │
      │                                      │
      │ Clock                                │
      │ Scheduler                            │
      │ AgentManager                         │
      │ MemoryManager                        │
      │ CrimeEngine                          │
      │ ConversationEngine                   │
      │ GossipEngine                         │
      │ EventBus                             │
      └──────────────────────────────────────┘
                         │
                         ▼
                  Court Engine
                         │
                         ▼
                      Verdict

---

# System Philosophy

Simulation always runs.

The player never pauses the world.

NPCs continuously:

- Observe
- Remember
- Gossip
- Change knowledge

The player only observes and influences.

---

# World

World is the root simulation object.

Responsibilities

- Advance simulation
- Own simulation managers
- Execute one simulation tick

World does not contain business logic.

Business logic belongs inside subsystem managers.

---

# Simulation Tick

One simulation tick executes:

1. Advance Clock
2. Execute Scheduler
3. Update Agents
4. Execute Gossip Tick
5. Publish Tick Event

No subsystem should bypass this lifecycle.

---

# Locations

Only two locations exist.

## Cafe

Purpose

- NPC gathering
- Conversations
- Gossip
- Crime scene
- Investigation

---

## Court

Purpose

- Evidence submission
- Verdict generation

No simulation occurs here except court evaluation.

---

# Agents

Agents represent autonomous citizens.

Each Agent owns only state.

Current state includes

- Identity
- Location
- Goal
- State

Knowledge is externalized through MemoryManager.

Agents never directly modify one another.

---

# Memory System

Memory is the fundamental knowledge representation.

Everything an NPC knows is represented as Memory.

Memory may originate from

- Observation
- Gossip
- Crime
- Player influence

Memories are immutable.

---

# Crime Engine

CrimeEngine owns the single ground truth.

Responsibilities

- Create crime
- Store ground truth
- Seed initial witness memories

Exactly one active crime exists in the MVP.

---

# Conversation Engine

ConversationEngine transfers memories.

It never generates dialogue.

Responsibilities

- Share one memory
- Prevent duplicate transfers

Nothing else.

---

# Gossip Engine

GossipEngine decides when conversations happen.

Responsibilities

- Group nearby agents
- Select deterministic conversation pairs
- Invoke ConversationEngine

GossipEngine never transfers memories itself.

---

# Investigation Service

Provides read-only access to the simulation.

Responsibilities

- Query agents
- Query memories
- Observe locations

This layer exists so multiple interfaces can reuse the same backend.

Clients include

- EchoShell
- Future frontend

---

# Evidence System

Evidence wraps immutable Memories.

EvidenceManager stores all evidence collected by the player.

CaseFile stores only the evidence chosen for court.

---

# Court Engine

CourtEngine evaluates one CaseFile.

Input

- Active Crime
- Submitted CaseFile

Output

- Verdict

CourtEngine never modifies simulation state.

---

# EventBus

Subsystem communication happens through EventBus.

Subsystems should prefer events over directly calling each other whenever practical.

---

# EchoShell

EchoShell is the primary interface.

The shell is NOT gameplay logic.

Responsibilities

- Parse commands
- Validate arguments
- Call backend services
- Display results

Business logic always lives inside backend services.

---

# Higher Self

The player acts as the Higher Self.

The player influences cognition rather than directly controlling NPCs.

Examples

- Suggest
- Remember
- Warn
- Observe
- Trace
- Connect

Higher Self operations modify simulation state indirectly.

---

# AI Integration

LLM is optional.

Simulation never depends on AI.

LLM responsibilities

- Dialogue
- Court explanation
- Interrogation
- Flavor text

Simulation responsibilities

- Crime
- Gossip
- Scheduling
- Memory
- Evidence
- Verdict

---

# Dependency Rules

Simulation layers may depend downward only.

EchoShell
        │
        ▼
Investigation Service
        │
        ▼
Simulation
        │
        ▼
Core Models

Never reverse this dependency direction.

---

# Architectural Rules

Every subsystem should:

- Have one responsibility.
- Expose a minimal public API.
- Own its own data.
- Avoid hidden side effects.

If two subsystems communicate,

prefer explicit method calls or events.

Never duplicate business logic.

---

# Definition of Done

The architecture is complete when:

- Simulation runs autonomously.
- Crime propagates through gossip.
- Player investigates through EchoShell.
- Court evaluates evidence.
- World continues after the verdict.

Everything else is polish.