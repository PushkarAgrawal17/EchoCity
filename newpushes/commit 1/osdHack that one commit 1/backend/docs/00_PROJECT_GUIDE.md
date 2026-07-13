# EchoCity - Project Guide

Version: 2.0

---

# Purpose

EchoCity is an offline AI-powered social investigation simulation built for a hackathon.

The goal is to build a believable, living AI city that demonstrates autonomous social behavior on-device. The investigation is the vehicle through which the player experiences that living city.

The goal is to create one believable investigation experience where autonomous AI-driven citizens interact, gossip, remember, and influence one another while the player subtly manipulates the world as the **Higher Self**.

Everything in this repository should support that objective.

---

# Core Vision

EchoCity is not about controlling characters.

It is about observing and influencing a living cognitive simulation.

NPCs should appear autonomous.

The player should feel like an unseen intelligence rather than a playable character.

---

# Design Philosophy

Always optimize for:

- Simplicity
- Determinism
- Offline execution
- Fast iteration
- Demo quality

Never optimize for:

- Maximum realism
- Generic frameworks
- Premature abstraction
- Scalability beyond the hackathon

---

# MVP Scope

The entire demo revolves around:

- One Cafe
- One Court
- One Crime
- Eight to ten NPCs
- One complete investigation

If a feature does not improve this experience, postpone it.

---

# Architecture Principles

Simulation drives gameplay.

AI enhances gameplay.

AI never replaces simulation.

Deterministic Python systems own:

- Crime
- Gossip
- Scheduling
- Memories
- Evidence
- Court evaluation

LLMs are optional enhancements.

---

# AI Philosophy

The project must remain fully playable without any LLM.

The simulation should continue running even if Ollama is unavailable.

LLMs are used only for:

- Dialogue
- Interrogation
- Court explanations
- Flavor text

Never use an LLM for:

- Scheduling
- World simulation
- Crime generation
- Memory propagation
- Core game logic

---

# Player Role

The player is the Higher Self.

The player cannot directly control NPCs.

Instead, the player subtly influences thoughts, memories and interactions using EchoShell.

The player observes more than they command.

---

# Development Principles

Build one subsystem at a time.

Every subsystem must:

- compile
- include tests
- pass linting
- pass type checking

before the next subsystem begins.

Never implement future milestones early.

---

# Coding Philosophy

Prefer:

- Small modules
- Clear interfaces
- Composition
- Immutable data
- Explicit behavior

Avoid:

- Hidden side effects
- Global mutable state
- Overengineering
- Large classes
- Deep inheritance

---

# Performance Goals

Target hardware:

Consumer laptops.

Target runtime:

Completely offline.

Target simulation:

8–10 NPCs running simultaneously.

Responsiveness is more important than realism.

---

# Non Goals

EchoCity is NOT attempting to build:

- An entire city simulation
- A life simulator
- A generic AI framework
- Multiplayer
- Complex economy
- Politics
- Inventory systems
- Procedural world generation
- Multiple simultaneous crimes

These may be future extensions but are outside the MVP.

---

# Definition of Success

A successful demo allows the player to:

- Observe the world
- Investigate one crime
- Influence NPC cognition
- Collect evidence
- Present a case
- Receive a deterministic verdict

The simulation should continue naturally before, during and after the investigation.

---

# Final Rule

Whenever a design decision is uncertain, choose the solution that produces the most polished playable demo within the hackathon time limit.

A finished small system is always better than an unfinished ambitious one.