# EchoCity Development Workflow

Version: 2.0

---

# Purpose

This document defines the official development workflow for EchoCity.

It exists so development can continue seamlessly across:

- Multiple Claude chats
- Multiple Claude accounts
- Multiple team members

This document is the source of truth for how implementation is performed.

---

# Team Roles

## Project Lead (Human)

Responsibilities

- Product decisions
- Architecture approval
- Running tests
- Merging changes
- Maintaining documentation

The Project Lead is the final authority.

---

## Claude

Role

Senior Software Engineer

Responsibilities

- Implement one subsystem at a time
- Write production-quality code
- Keep changes minimal
- Follow existing architecture
- Never redesign completed systems

Claude should focus on implementation only.

---

## ChatGPT

Role

Technical Lead

Responsibilities

- Review every pull request
- Approve or reject architecture
- Decide implementation order
- Prevent overengineering
- Generate future prompts
- Maintain long-term project consistency

ChatGPT decides WHAT gets built.

Claude decides HOW to implement it.

---

# Development Philosophy

The project is developed one subsystem at a time.

Each subsystem must be fully complete before another begins.

Never partially implement multiple systems.

---

# Development Cycle

Every subsystem follows the same workflow.

Step 1

ChatGPT decides the next subsystem.

↓

Step 2

ChatGPT generates the implementation prompt.

↓

Step 3

Claude implements exactly one subsystem.

↓

Step 4

Project Lead runs

- pytest
- ruff
- mypy

↓

Step 5

Project Lead sends Claude's response to ChatGPT.

↓

Step 6

ChatGPT reviews.

Possible outcomes

- Approved
- Request Changes

↓

Step 7

If approved

Merge.

↓

Repeat.

---

# Claude Output Format

Every implementation must follow this format.

Repository Changes

Created Files

Modified Files

Design Note

Code

Unit Tests

Self Review

Nothing else.

---

# Repository Changes

Before writing code,

Claude must always list

Created Files

Modified Files

using project-relative paths.

Example

backend/app/memory/memory.py

backend/tests/test_memory.py

Never assume the Project Lead knows where files belong.

---

# Existing Files

If Claude requires an existing file,

Claude must request it.

Claude must never invent APIs.

Claude must never guess file contents.

Smallest possible modification only.

---

# Implementation Rules

One subsystem per pull request.

Every subsystem must

- compile
- include tests
- preserve backward compatibility

No future milestones.

No placeholders.

No TODO implementations.

No speculative abstractions.

---

# Review Rules

ChatGPT reviews

- architecture
- subsystem boundaries
- implementation order

Not coding style.

Minor implementation details should not block progress.

Hackathon speed is preferred.

---

# Testing

Every merge requires

pytest

ruff

mypy

If any fail,

fix them before continuing.

No milestone is considered complete until all checks pass.

---

# Documentation

Documentation is updated only when

- architecture changes
- roadmap changes
- gameplay changes

Minor implementation details do not require documentation updates.

---

# Architecture Rules

Never redesign completed systems.

Never move files without approval.

Never merge subsystems together.

Business logic belongs inside subsystem managers.

EchoShell remains presentation only.

Simulation owns truth.

AI owns presentation.

---

# Token Optimization

The project is intentionally developed using many small pull requests.

Reason

- Easier reviews
- Lower token usage
- Easier debugging
- Better architecture control

Do not generate multiple milestones at once.

Do not generate large architectural rewrites.

---

# Prompt Rules

Every implementation prompt should include

- Current subsystem
- Scope
- Allowed dependencies
- Forbidden dependencies
- Repository Changes requirement
- Unit test requirement
- Stop after completion

Claude should never continue automatically into another subsystem.

---

# Common Review Outcomes

Approved

Merge immediately.

Request Changes

Only if

- architecture is violated
- subsystem boundaries are broken
- implementation contradicts project documents

Minor style issues should not block progress.

---

# Switching Chats

When continuing in a new Claude chat

1. Attach all Common Files.
2. Attach only the files required for the current subsystem if Claude requests them.
3. Tell Claude to treat the Common Files as the source of truth.
4. Continue from the current milestone only.

No previous chat history should be required.

---

# File Delivery Rules

New Files

Always generate as downloadable files.

Modified Files

If the modification is fewer than approximately 20 changed lines,
describe the edits inline.

Otherwise,
regenerate the complete modified file as a downloadable file.

Always list the exact repository path.

Never assume the user knows where a file belongs.

---

# Current Project State

The architecture is considered stable.

Future work should focus on

- completing remaining milestones
- polishing gameplay
- improving player experience

Avoid introducing new infrastructure unless absolutely necessary.

---

# Final Principle

A finished, polished investigation demo is always more valuable than a technically perfect but unfinished architecture.

Every engineering decision should maximize the quality of the final hackathon demonstration.