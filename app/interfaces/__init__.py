"""Interfaces for dependency injection and abstraction."""

from .llm import ILLMProvider
from .logger import ILogger
from .config import IConfig
from .sandbox import ISandboxClient

__all__ = [
    "ILLMProvider",
    "ILogger", 
    "IConfig",
    "ISandboxClient",
]