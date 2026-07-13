# EchoCity Coding Standards

Version: 1.0

---

# Purpose

This document defines the coding standards used throughout EchoCity.

Every contributor, whether human or AI, must follow these conventions.

The objective is consistency, maintainability, readability, and production-quality code.

---

# General Philosophy

Readable code is better than clever code.

Correct code is better than optimized code.

Simple code is better than complex code.

Maintainable code is better than short code.

Consistency is more important than personal preference.

---

# Python Version

Python 3.12+

Do not use features requiring a newer version unless explicitly approved.

---

# Code Style

Follow

PEP 8

Use

Black formatting

isort

ruff

mypy

Recommended maximum line length

100 characters

---

# Naming Conventions

## Classes

PascalCase

Examples

World

AgentManager

MemoryManager

ConversationService

DecisionEngine

---

## Functions

snake_case

Examples

update_world()

retrieve_memory()

broadcast_event()

---

## Variables

snake_case

Examples

current_goal

agent_state

memory_score

---

## Constants

UPPER_CASE

Examples

SIMULATION_TICK

DEFAULT_SPEED

MAX_MEMORY_RESULTS

---

## Private Members

Prefix with

_

Example

_load_memories()

_internal_cache

---

# Imports

Order

Standard Library

↓

Third-party Packages

↓

Local Modules

Example

import asyncio
from pathlib import Path

from fastapi import FastAPI

from app.simulation.world import World

Never use wildcard imports.

---

# Type Hints

Every public function must use type hints.

Good

def update_agent(agent: Agent) -> None:

Bad

def update_agent(agent):

---

# Docstrings

Every public class

must have

a meaningful docstring.

Explain

Purpose

Responsibilities

Usage

Avoid obvious comments.

Good

"""Manages all active agents in the simulation."""

Bad

"""Agent Manager"""

---

# Comments

Write comments only when explaining

Why

not

What

Bad

x += 1  # increment x

Good

# Skip inference when deterministic behavior is sufficient.

---

# File Size

Maximum

300 lines

If a file grows beyond

400 lines

consider splitting it.

---

# Function Size

Maximum

40 lines

Large functions should be decomposed into helper functions.

---

# Class Size

Each class should own

one responsibility.

If a class begins managing multiple systems,

split it.

---

# Dependency Rules

Never create circular imports.

Never import upward.

Example

Allowed

services

↓

repositories

↓

database

Not Allowed

database

↓

services

---

# Error Handling

Catch only exceptions you can handle.

Never write

except:

Always write

except ValueError:

Log unexpected exceptions.

Fail gracefully.

---

# Logging

Use

logging

Never use

print()

Log Levels

DEBUG

INFO

WARNING

ERROR

CRITICAL

Every subsystem owns its own logger.

---

# Async Rules

Use async only for

Network IO

Database IO

WebSockets

LLM requests

Do not make CPU-heavy code async.

---

# SQLAlchemy

Always use ORM models.

Never write raw SQL unless performance requires it.

Use repositories.

Never expose ORM models directly to the frontend.

---

# FastAPI

Keep endpoints thin.

Endpoints should

Validate

↓

Call Service

↓

Return Response

Business logic belongs in services.

---

# WebSockets

Broadcast events.

Never broadcast entire world state.

Send only

Movement

Conversation

Relationship

News

Evidence

Events

---

# Event System

Never directly modify another subsystem.

Always publish an event.

Wrong

relationship_manager.update()

Correct

publish(RelationshipUpdated(...))

---

# AI

Never call Ollama directly.

Always use

Decision Engine

↓

Inference Queue

↓

LLM Adapter

---

# SQLite

Never access SQLite directly.

Always use repositories.

Repositories own persistence.

---

# Testing

Every public module should have tests.

Priority

Unit Tests

↓

Integration Tests

↓

Simulation Tests

---

# Git Branches

main

Stable

develop

Integration

feature/<feature-name>

Implementation

fix/<bug-name>

Bug fixes

---

# Commit Messages

Follow Conventional Commits.

Examples

feat: implement scheduler

fix: resolve event dispatch race

docs: update architecture

refactor: simplify world engine

perf: reduce llm calls

test: add scheduler tests

chore: update dependencies

---

# Pull Request Checklist

Architecture respected

Code compiles

Tests pass

Formatting passes

No dead code

No TODO placeholders

Documentation updated

Performance considered

Self-review completed

---

# Code Review Checklist

Review

Architecture

Readability

Maintainability

Performance

Error Handling

Naming

Logging

Type Hints

Testing

Dependencies

SOLID

---

# Performance Guidelines

Prefer deterministic logic.

Minimize allocations.

Avoid duplicate work.

Cache expensive computations.

Never block the simulation.

Batch persistence.

Limit LLM usage.

---

# Definition of Done

A feature is complete only if

Architecture respected

Code reviewed

Tests passing

Documentation updated

Performance acceptable

No obvious refactoring required

Project builds successfully

---

# Rules For Claude

Always explain implementation before coding.

Always review generated code.

Suggest improvements when appropriate.

Prefer maintainable architecture over clever implementations.

Never generate code that violates these standards.

If uncertain,

ask before implementing.

Act as a Senior Software Engineer,

not as a code generator.