"""Dependency injection foundation.

EchoCity uses FastAPI's built-in ``Depends`` mechanism rather than a custom
DI container. This module exposes the small set of dependencies shared
across the whole API. As real subsystems are introduced (World, EventBus,
DatabaseService, ...) their providers will be added here, each one
constructed once and shared, never as global mutable module state.
"""

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]
