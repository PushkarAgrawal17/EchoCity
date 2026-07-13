# EchoCity Implementation Guide

Version: 1.0

---

# Purpose

This document defines how EchoCity should be implemented.

It does NOT define architecture.

It defines the engineering workflow.

Claude must follow this workflow before writing any code.

The goal is to produce maintainable, production-quality software rather than simply generating working code.

---

# Engineering Philosophy

EchoCity is built like a production software project.

Not like a hackathon prototype.

Every implementation decision should prioritize

- readability
- modularity
- maintainability
- testability
- performance

over writing the shortest code possible.

---

# Golden Rule

Never generate the entire project.

Implement exactly one milestone at a time.

Each milestone must compile successfully before continuing.

---

# Engineering Workflow

Every milestone follows this sequence.

## Step 1

Understand the milestone.

Clarify

- requirements
- dependencies
- scope

Never implement features belonging to future milestones.

---

## Step 2

Review architecture.

Before writing code,

explain

- responsibilities
- dependencies
- module interactions

Only then begin implementation.

---

## Step 3

Implementation

Write production-quality code.

Prefer clarity over cleverness.

---

## Step 4

Review

After implementation

review the code as a Senior Software Engineer.

Look for

- coupling
- duplication
- unnecessary abstractions
- performance issues
- future scalability

Refactor if necessary.

---

## Step 5

Verification

Ensure

- project runs
- tests pass
- lint passes
- architecture remains unchanged

---

# Folder Rules

Every folder owns exactly one subsystem.

Do not mix responsibilities.

Correct

simulation/

agents/

events/

database/

Incorrect

utils/

misc/

helpers/

god/

---

# File Rules

Maximum file size

Approximately 300 lines.

If a file grows larger,

split it.

---

# Function Rules

Functions should

- perform one task
- be easy to test
- avoid side effects

Avoid

500-line functions.

---

# Class Rules

Each class owns one responsibility.

Examples

World

Owns simulation.

Scheduler

Owns scheduling.

Agent

Owns NPC state.

MemoryManager

Owns memories.

Never combine responsibilities.

---

# Dependency Rules

Always depend downward.

Allowed

World

↓

Scheduler

↓

AgentManager

↓

Agent

Not Allowed

Agent

↓

FastAPI

Agent

↓

SQLite

Frontend

↓

Database

---

# Module Communication

Prefer

Events

↓

Services

↓

Interfaces

Avoid

Direct object manipulation.

---

# Naming Rules

Classes

PascalCase

World

MemoryManager

ConversationService

Variables

snake_case

current_location

current_goal

Functions

snake_case

update_world()

retrieve_memory()

Constants

UPPER_CASE

DEFAULT_SPEED

SIMULATION_TICK

---

# Type Hints

Every public function

must use

type hints.

Example

def update_agent(agent: Agent) -> None

---

# Docstrings

Every public class

must contain

a meaningful docstring.

Explain

- purpose
- responsibility
- usage

Avoid useless comments.

---

# Logging

Use logging.

Never use print().

Every subsystem owns its own logger.

Log

Startup

Shutdown

Errors

Warnings

Critical simulation events

---

# Error Handling

Every subsystem should fail independently.

LLM failure

↓

Conversation unavailable

↓

Simulation continues

Database failure

↓

Graceful shutdown

↓

Useful logs

Never silently ignore exceptions.

---

# Code Review Checklist

Before considering a milestone complete,

review

Architecture

Performance

Readability

Naming

Dependencies

SOLID Principles

Type Hints

Docstrings

Logging

Error Handling

Unused Code

Dead Imports

Circular Imports

Large Files

Long Functions

---

# Performance Checklist

Never optimize prematurely.

First

Make it correct.

Second

Make it clean.

Third

Optimize.

Optimization priorities

Reduce LLM calls.

Reduce database writes.

Use caching.

Keep runtime state in RAM.

Batch persistence.

Avoid unnecessary allocations.

---

# Git Workflow

One milestone

↓

One feature branch

↓

One pull request

↓

One review

↓

Merge

Small commits are preferred.

Commit messages

feat:

fix:

refactor:

docs:

test:

perf:

chore:

---

# Testing Rules

Each module should be testable independently.

Recommended order

Unit Tests

↓

Module Tests

↓

Integration Tests

↓

Manual Simulation

Do not skip manual verification.

---

# Documentation Rules

Every milestone must update

README

Architecture

Roadmap

if required.

Documentation is part of the implementation.

---

# Definition of Done

A milestone is complete only if

Architecture respected

Code compiles

Tests pass

No TODO placeholders

No unused code

No dead imports

No obvious refactoring needed

Documentation updated

Review completed

---

# Rules For Claude

Before writing code

Explain the implementation plan.

After writing code

Review it critically.

If a better design exists,

suggest it.

Do not blindly generate code.

Act as a Senior Software Engineer reviewing every pull request.

Always favor maintainability over speed.

Never sacrifice architecture for convenience.