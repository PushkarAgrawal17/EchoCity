# EchoCity Architecture Decisions

Version: 1.0

---

# Purpose

This document records important architectural decisions made during the development of EchoCity.

Unlike implementation documents, this file explains **why** decisions were made.

Future contributors should consult this document before proposing architectural changes.

---

# ADR-001

Decision

EchoCity is an investigation game, not a city simulator.

Reason

The hackathon lasts only five days.

Building one polished investigation experience provides significantly more value than attempting a full city simulation.

---

# ADR-002

Decision

The player is the Higher Self rather than a detective.

Reason

This creates a unique gameplay mechanic aligned with the AI-on-device theme.

The player influences cognition instead of directly controlling characters.

---

# ADR-003

Decision

The primary interface is EchoShell.

Reason

The shell naturally exposes observation and cognitive influence commands.

Future graphical interfaces will become clients of the same backend instead of containing gameplay logic.

---

# ADR-004

Decision

Simulation owns truth.

AI owns presentation.

Reason

Deterministic simulation guarantees correctness.

LLMs improve immersion without affecting gameplay.

The game remains fully playable when AI is unavailable.

---

# ADR-005

Decision

Use exactly one local LLM.

Reason

Running one model is significantly faster and lighter than maintaining one model per NPC.

Every NPC shares the same inference engine while maintaining different internal state.

---

# ADR-006

Decision

Everything must work offline.

Reason

The project targets the AI On Device hackathon.

Internet access must never be required.

---

# ADR-007

Decision

Crime generation is deterministic.

Reason

The investigation must always have one objectively correct solution.

Random crimes reduce testability and demo reliability.

---

# ADR-008

Decision

Exactly one active crime exists.

Reason

A single polished scenario is preferable to multiple unfinished investigations.

---

# ADR-009

Decision

Only two locations exist.

Cafe

Court

Reason

The MVP focuses entirely on investigation.

Additional locations add complexity without improving the demo.

---

# ADR-010

Decision

Knowledge is represented as immutable Memory objects.

Reason

Memories become the single source of truth for information propagation.

Immutable data greatly simplifies debugging.

---

# ADR-011

Decision

Memory is owned by MemoryManager.

Reason

Agents remain lightweight.

Knowledge storage stays centralized.

Future interfaces can query memories independently of Agents.

---

# ADR-012

Decision

Conversation transfers memories.

Reason

Conversation should never generate information.

It simply propagates existing knowledge.

---

# ADR-013

Decision

Gossip decides when conversations happen.

Conversation decides how memories transfer.

Reason

Separating orchestration from transfer logic keeps both systems simple and reusable.

---

# ADR-014

Decision

Evidence wraps Memory.

Reason

Memory remains the canonical representation of knowledge.

Evidence is simply a player-facing interpretation of selected memories.

---

# ADR-015

Decision

EvidenceManager and CaseFile are separate systems.

Reason

EvidenceManager stores everything collected.

CaseFile stores only the evidence intentionally presented in court.

This mirrors real investigations.

---

# ADR-016

Decision

InvestigationService is read-only.

Reason

EchoShell and future frontends should reuse the same backend query layer.

Interfaces never contain gameplay logic.

---

# ADR-017

Decision

World owns the simulation managers.

Reason

Although a SimulationRuntime abstraction could reduce coupling, introducing it during the hackathon would increase complexity without improving the demo.

This tradeoff intentionally favors delivery speed.

---

# ADR-018

Decision

No database persistence for the MVP.

Reason

The simulation exists only during a single demo session.

Persistence adds complexity without improving gameplay.

---

# ADR-019

Decision

No relationship graph during the MVP.

Reason

Relationships improve realism but are not required to complete the investigation loop.

They remain a post-hackathon extension.

---

# ADR-020

Decision

No emotion system during the MVP.

Reason

Dialogue quality is sufficient for the hackathon.

Emotions increase implementation complexity without affecting the core mechanics.

---

# ADR-021

Decision

Backend development proceeds one subsystem at a time.

Reason

Small pull requests simplify reviews, testing, and architectural consistency.

---

# ADR-022

Decision

Every subsystem must pass pytest, mypy and ruff before merge.

Reason

The repository should remain stable after every milestone.

No milestone is considered complete while tests fail.

---

# ADR-023

Decision

Claude implements.

ChatGPT reviews.

Reason

Separating implementation from architectural review reduces design drift and keeps development consistent across multiple chats and accounts.

---

# ADR-024

Decision

Repository documentation is the project's source of truth.

Reason

Chats are temporary.

Documentation is permanent.

Any new Claude session should be able to continue development using only the repository documentation.

---

# Future ADRs

Any architectural decision that changes:

- gameplay
- subsystem boundaries
- AI usage
- simulation rules
- development workflow

should be recorded here before implementation.

This document preserves the reasoning behind the project, not just the code.