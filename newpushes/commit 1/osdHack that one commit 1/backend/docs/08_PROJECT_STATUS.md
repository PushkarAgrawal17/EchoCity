# EchoCity Project Status

Version: 3.0

---

# Current Goal

Build a believable, fully offline living city where autonomous AI citizens
observe, remember, gossip, influence one another, and continue living
independently of the player.

The investigation exists to reveal the city's emergent behavior—not to
script it.

---

# Overall Progress

Core simulation systems are complete.

The world now supports

- deterministic simulation
- autonomous agents
- persistent memories
- crime generation
- conversations
- rumor propagation
- investigation
- evidence collection
- court evaluation
- playable shell
- demo bootstrap

The backend is now capable of running one complete investigation without
requiring any AI model.

---

# Completed Systems

## Foundation

✓ Project structure

✓ Configuration

✓ Testing infrastructure

---

## Simulation

✓ World

✓ Simulation Engine

✓ Clock

✓ Scheduler

✓ Event Bus

---

## Agents

✓ Agent

✓ Agent Manager

✓ Agent State

---

## Locations

✓ Location

✓ Location Manager

---

## Memory

✓ Memory

✓ Memory Manager

---

## Crime

✓ Crime

✓ Crime Engine

✓ Witness memory seeding

---

## Conversations

✓ Conversation

✓ Conversation Engine

---

## Gossip

✓ Gossip Engine

✓ Deterministic rumor propagation

✓ Rotating conversation pairing

---

## Investigation

✓ Investigation Service

---

## Evidence

✓ Evidence

✓ Evidence Manager

✓ Case File

---

## Court

✓ Court Engine

✓ Verdict evaluation

---

## Bootstrap

✓ GameFactory

✓ Demo world construction

✓ Initial rumor propagation

---

## Shell

✓ EchoShell

✓ Navigation commands

✓ Investigation commands

✓ Court commands

✓ Interactive demo

---

# Current Milestone

## Higher Self

Next objective

Allow the player to influence cognition without directly controlling NPCs.

Planned abilities include

- Suggest
- Remember
- Encourage
- Comfort
- Warn
- Connect
- Coincidence

The player should manipulate beliefs rather than actions.

---

# Remaining Milestones

- Higher Self cognition
- LLM dialogue generation
- Natural interrogation
- Court explanations
- Demo polish
- Frontend

---

# Current State

The city can already

- simulate autonomous citizens
- create a deterministic crime
- seed witness memories
- spread rumors
- allow player investigation
- collect evidence
- evaluate accusations

The remaining work focuses on making the citizens feel increasingly alive rather than adding more game mechanics.

---

# Definition of MVP

The MVP is complete when a player can

watch a living city,

observe information spreading naturally,

subtly influence the citizens,

investigate a crime,

and understand why the final verdict occurred,

all while running entirely offline.