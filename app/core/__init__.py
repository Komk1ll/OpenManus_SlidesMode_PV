"""Core module for presentation system architecture.

This module provides base abstractions and interfaces for the presentation system,
including executors, middleware, event handling, and configuration management.
"""

from .base_executor import BaseExecutor
from .base_middleware import BaseMiddleware
from .event_bus import EventBus, Event
from .config_manager import ConfigManager
from .tool_registry import ToolRegistry

__all__ = [
    "BaseExecutor",
    "BaseMiddleware", 
    "EventBus",
    "Event",
    "ConfigManager",
    "ToolRegistry"
]