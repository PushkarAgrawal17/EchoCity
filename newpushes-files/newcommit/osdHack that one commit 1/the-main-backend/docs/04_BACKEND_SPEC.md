# EchoCity Backend Blueprint

Version: 1.0

---

# Purpose

This document defines the backend architecture of EchoCity.

It is the authoritative reference for backend implementation.

Every backend module, service, class, and package should follow this specification.

Backend architecture must remain modular, testable, and independent from the frontend.

---

# Backend Philosophy

EchoCity is NOT a CRUD application.

EchoCity is a real-time simulation.

FastAPI exists only to expose the simulation.

The simulation itself should be able to run without FastAPI.

The backend should be divided into independent systems.

Each system owns one responsibility.

---

# Technology Stack

Language

Python 3.12

Framework

FastAPI

Database

SQLite

ORM

SQLAlchemy 2.0

Migration

Alembic

Async

AsyncIO

Realtime

WebSockets

AI Runtime

Ollama

Package Manager

uv

---

# Repository Structure

backend/

app/

├── api/

├── core/

├── simulation/

├── agents/

├── events/

├── memory/

├── database/

├── llm/

├── websocket/

├── workers/

├── services/

├── models/

├── utils/

└── main.py

Every directory should represent exactly one subsystem.

---

# Module Responsibilities

## api/

Contains

REST endpoints

WebSocket endpoints

Request validation

Response models

API should NEVER contain business logic.

---

## core/

Contains

Configuration

Environment

Logging

Application startup

Constants

Dependency Injection

---

## simulation/

Contains

World

Clock

Scheduler

SimulationEngine

TickManager

SimulationRunner

This is the heart of the project.

---

## agents/

Contains

Agent

AgentManager

StateMachine

Navigation

GoalPlanner

EmotionEngine

RelationshipEngine

Agents must never directly access FastAPI or SQLite.

---

## events/

Contains

Event models

EventBus

Publishers

Subscribers

Dispatchers

Every module communicates through events.

---

## memory/

Contains

MemoryManager

MemoryRanking

MemoryRetrieval

MemoryPersistence

Conversation summaries

No direct LLM calls.

---

## llm/

Contains

Ollama client

Prompt builder

Inference Queue

Response validation

JSON parser

LLM is treated as an external reasoning engine.

---

## database/

Contains

Database session

Repositories

ORM Models

Migrations

Persistence layer only.

---

## websocket/

Contains

ConnectionManager

BroadcastService

Subscriptions

Realtime updates

---

## workers/

Contains

Background tasks

LLM workers

Save workers

Cleanup workers

Never place business logic here.

---

## services/

Contains

Business orchestration.

Example

ConversationService

InvestigationService

CourtService

CrimeService

Services coordinate modules.

---

## utils/

Contains

Generic helper functions.

No business logic.

---

# Core Objects

World

Clock

Scheduler

AgentManager

MemoryManager

EventBus

DecisionEngine

DatabaseService

ConnectionManager

SimulationEngine

These are the only high-level objects.

---

# World Ownership

World owns

Clock

Scheduler

AgentManager

EventBus

MemoryManager

DecisionEngine

DatabaseService

World is responsible for advancing the simulation.

No other module may advance time.

---

# Simulation Lifecycle

Simulation Start

↓

Load World

↓

Load Agents

↓

Initialize Scheduler

↓

Start Tick Loop

↓

Simulation Running

↓

Player Interaction

↓

Save World

↓

Shutdown

---

# Tick Lifecycle

Each simulation tick executes

Update Clock

↓

Execute Scheduled Tasks

↓

Update Agent States

↓

Publish Events

↓

Dispatch Events

↓

Persist Changes

↓

Broadcast Updates

Every phase must complete before the next begins.

---

# Service Layer

Services coordinate multiple modules.

ConversationService

Coordinates

Agent

Memory

LLM

Events

WebSocket

CrimeService

Coordinates

Crime

Evidence

Events

Court

Memory

Services do NOT store state.

---

# Repository Pattern

Each persistent model has one repository.

Example

AgentRepository

MemoryRepository

RelationshipRepository

EventRepository

DiaryRepository

Repositories hide SQLAlchemy.

The rest of the application never writes SQL directly.

---

# Dependency Rules

Allowed

World

↓

AgentManager

↓

Agent

Allowed

ConversationService

↓

MemoryManager

↓

LLM

Not Allowed

Agent

↓

FastAPI

Not Allowed

Agent

↓

SQLite

Not Allowed

Frontend

↓

Database

Communication always flows downward.

---

# Database Rules

SQLite is persistence.

Simulation state remains in RAM.

Write only

Important Memories

Relationships

Cases

Evidence

Diaries

Player Progress

Avoid writing transient data every tick.

---

# LLM Rules

LLM is expensive.

Never invoke Ollama for

Movement

Schedules

Navigation

Idle behavior

Simple state transitions

Use Ollama only for

Dialogue

Planning

Interrogation

Court

Diary

Major decisions

All requests pass through the Inference Queue.

---

# API Rules

FastAPI only exposes the simulation.

Typical endpoints

GET /world

GET /agents

GET /events

POST /command

WS /live

Never expose internal implementation.

---

# Error Handling

Every subsystem should fail independently.

Example

LLM failure

↓

Conversation unavailable

↓

Simulation continues

Example

WebSocket disconnect

↓

Frontend disconnects

↓

Simulation continues

Simulation must never stop because one subsystem failed.

---

# Logging

Every subsystem owns a logger.

Log

Startup

Shutdown

Errors

Warnings

Important Events

Never print() in production code.

---

# Testing Strategy

Each module should be independently testable.

Simulation tests

Repository tests

Agent tests

Event tests

Service tests

Avoid integration testing until individual modules work.

---

# Coding Rules

One class

One responsibility

One module

One responsibility

Prefer composition over inheritance.

Avoid circular imports.

Avoid singleton objects.

No global mutable state.

Use dependency injection.

Every public function should contain type hints.

Every public class should contain docstrings.

---

# Definition of Done

The backend is considered complete when

Simulation runs independently.

Agents live autonomously.

Events propagate correctly.

SQLite persists important state.

WebSockets broadcast changes.

Player commands influence the world.

Frontend contains no business logic.

The simulation continues even if the frontend disconnects.

The simulation continues even if the LLM becomes unavailable.

---

# Rules For Claude

Always preserve this architecture.

Never introduce unnecessary abstractions.

Never generate giant files.

Prefer small reusable modules.

Prefer interfaces over tightly coupled implementations.

Always explain architectural decisions before implementation.

If implementation conflicts with this blueprint,

update the blueprint first,

then implement the change.