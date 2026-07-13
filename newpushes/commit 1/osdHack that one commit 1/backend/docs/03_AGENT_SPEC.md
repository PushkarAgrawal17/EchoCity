# EchoCity Development Roadmap

Version: 2.0

---

# Purpose

This document defines the official implementation order for EchoCity.

Every subsystem depends on previous milestones.

Never skip milestones.

Never implement future milestones early.

---

# Development Philosophy

EchoCity is developed as one complete vertical slice.

The objective is to produce one polished investigation experience.

Not a generic simulation framework.

Every subsystem must directly contribute to the final gameplay loop.

---

# Completed Milestones

## Milestone 0

Project Foundation

Completed

- Repository structure
- FastAPI
- Configuration
- Logging
- Dependency Injection
- Testing infrastructure

Status

✅ Complete

---

## Milestone 1

Simulation Core

Completed

- World
- SimulationEngine
- Clock
- Scheduler
- EventBus
- Agent
- AgentManager

Status

✅ Complete

---

## Milestone 2

Location System

Completed

- Location
- LocationType
- LocationManager

Status

✅ Complete

---

## Milestone 3

Memory System

Completed

- Memory
- MemoryType
- MemoryManager

Status

✅ Complete

---

## Milestone 4

Crime Engine

Completed

- Crime
- CrimeStatus
- CrimeEngine

Status

✅ Complete

---

## Milestone 5

Conversation System

Completed

- Conversation
- ConversationEngine

Status

✅ Complete

---

## Milestone 6

Automatic Gossip

Completed

- GossipEngine

Status

✅ Complete

---

## Milestone 7

Investigation Layer

Completed

- InvestigationService

Status

✅ Complete

---

## Milestone 8

Evidence System

Completed

- Evidence
- EvidenceManager

Status

✅ Complete

---

## Milestone 9

Case File

Completed

- CaseFile

Status

✅ Complete

---

# Current Milestone

## Milestone 10

Court Engine

Goal

Evaluate the player's submitted evidence.

Deliverables

- Verdict
- CourtEngine

Output

Win or Lose.

Nothing else.

Status

🚧 In Progress

---

# Remaining Milestones

## Milestone 11

EchoShell

Deliverables

Core shell

Commands

- help
- ls
- cd
- pwd
- tree
- observe
- question
- trace
- collect
- submit
- accuse

Goal

Playable investigation.

---

## Milestone 12

Higher Self Operations

Deliverables

Commands

- suggest
- remember
- encourage
- comfort
- warn
- connect
- coincidence

Goal

Player can influence cognition without directly controlling NPCs.

---

## Milestone 13

LLM Integration

Deliverables

Ollama Runtime

Uses

- Dialogue
- Court explanation
- Interrogation

Never

- Crime
- Scheduling
- Gossip
- Simulation

LLM remains optional.

---

## Milestone 14

Demo Polish

Deliverables

- NPC roster
- Better console output
- Logging improvements
- README
- Screenshots
- Demo script
- Performance tuning

---

# Milestone Rules

Every milestone must

- compile
- include tests
- pass pytest
- pass ruff
- pass mypy

before the next milestone begins.

---

# Definition of MVP

The MVP is complete when:

Simulation starts.

↓

NPCs gossip.

↓

Crime occurs.

↓

Player investigates.

↓

Evidence collected.

↓

Case submitted.

↓

Court returns verdict.

↓

Simulation continues.

---

# Stretch Goals

Only if time remains.

Possible additions

- Relationships
- Stress
- Confidence
- Emotion
- Multiple crimes
- Additional locations
- Pixel city visualization
- Diary generation
- Better AI prompts

None of these are required for the hackathon.

---

# Forbidden During MVP

Do NOT implement

- Multiple cities
- Economy
- Politics
- Multiplayer
- Inventory
- Generic planning engine
- Autonomous pathfinding
- Database persistence
- Complex relationship graphs

These are intentionally postponed.

---

# Final Rule

If a feature does not improve the MVP investigation loop,

it should not be implemented during the hackathon.