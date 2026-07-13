# EchoCity AI Runtime

Version: 2.0

---

# Purpose

This document defines how AI is used inside EchoCity.

EchoCity is an AI-assisted simulation.

It is NOT an LLM-driven simulation.

The simulation must function completely offline and remain fully playable even if no LLM is available.

---

# Design Philosophy

Simulation owns reality.

AI owns language.

Simulation decides:

- What happened.
- What NPCs know.
- What NPCs remember.
- What NPCs share.
- Who committed the crime.
- Whether evidence is correct.

AI decides only:

- How information is expressed.
- How NPCs speak.
- How Court explains its verdict.

---

# Runtime Goals

The project targets:

- Consumer laptops
- Offline execution
- Ollama
- One local language model

No internet connection should ever be required.

---

# AI Usage Policy

The LLM is OPTIONAL.

Every gameplay feature must continue functioning if the LLM is disabled.

Fallback responses should always exist.

---

# When AI SHOULD be used

Only invoke the LLM for:

## Dialogue

NPC conversations with the player.

Example

Player

Question Emma

↓

Simulation retrieves Emma's memories

↓

LLM converts memories into natural dialogue

---

## Interrogation

NPC explains

- what they saw
- what they believe
- what they heard

The LLM never invents new facts.

---

## Court Explanation

After a verdict,

the LLM may explain

- why the player succeeded
- why the evidence failed

The Verdict itself remains deterministic.

---

## Flavor Text

Optional

- observations
- descriptions
- atmosphere

---

# When AI MUST NOT be used

Never invoke the LLM for

- Crime generation
- Memory propagation
- Gossip
- Scheduling
- World updates
- Agent movement
- Pair selection
- Evidence validation
- Verdict generation
- Simulation timing

These remain deterministic Python systems.

---

# Single Model

EchoCity uses exactly one local model.

Example

Ollama

↓

Gemma

or

Llama

or

Qwen

No per-agent models.

No multiple inference pipelines.

---

# Runtime Flow

Player asks question

↓

Simulation retrieves memories

↓

Prompt Builder

↓

LLM

↓

Natural language response

↓

Displayed to player

The simulation itself never changes during inference.

---

# Prompt Construction

The prompt should contain

Identity

Known memories

Current location

Current goal

Conversation context

Nothing else.

Never dump the entire world state.

---

# Context Window

Only include

- Relevant memories
- Relevant facts
- Current conversation

Do not include unrelated information.

---

# Caching

Responses may be cached.

Cache key

Agent ID

+

Memory Hash

+

Question

If nothing changed,

reuse the cached response.

---

# Timeout Policy

LLM responses should never block the simulation indefinitely.

If inference exceeds timeout,

fallback to deterministic dialogue.

---

# Failure Policy

If Ollama

- crashes
- is unavailable
- times out

EchoCity continues running.

Only dialogue quality degrades.

Gameplay never stops.

---

# Future Optimization

Possible improvements

- Prompt compression
- Memory summarization
- Streaming responses
- Quantized models
- Better caching

These are optional.

---

# Performance Targets

Average dialogue response

< 2 seconds

Simulation Tick

< 50 ms

Memory sharing

< 1 ms

Court evaluation

Instant

---

# Non Goals

No

- multi-agent LLM architecture
- per-agent models
- autonomous planning
- tool-using agents
- online APIs
- cloud inference

---

# Definition of Success

A successful AI runtime:

- works fully offline
- never blocks simulation
- never owns game logic
- produces believable dialogue
- gracefully falls back when unavailable

Simulation always remains the source of truth.