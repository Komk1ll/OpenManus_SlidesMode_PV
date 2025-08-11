"""Executor module for presentation generation.

Provides execution orchestration, lifecycle management,
and streaming capabilities for presentation tools.
"""

from .presentation_executor import (
    PresentationExecutor,
    PresentationRequest,
    PresentationResponse,
    StreamingChunk,
    ExecutionMode
)

__all__ = [
    'PresentationExecutor',
    'PresentationRequest', 
    'PresentationResponse',
    'StreamingChunk',
    'ExecutionMode'
]