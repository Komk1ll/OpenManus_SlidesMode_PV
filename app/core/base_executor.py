"""Base executor class for orchestrating tool execution.

Provides the foundation for managing tool lifecycle, error handling,
and execution flow in the presentation system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, AsyncIterator
from dataclasses import dataclass
import asyncio
import logging
from contextlib import asynccontextmanager

from ..tool.base import BaseTool, ToolResult
from .event_bus import EventBus, Event
from .base_middleware import BaseMiddleware

T = TypeVar('T')

@dataclass
class ExecutionContext:
    """Context for tool execution with metadata and state."""
    session_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ExecutionResult(Generic[T]):
    """Result of tool execution with success/failure information."""
    success: bool
    result: Optional[T] = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseExecutor(ABC):
    """Base class for tool execution orchestration.
    
    Provides common functionality for managing tool execution,
    middleware processing, event handling, and error management.
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.event_bus = event_bus or EventBus()
        self.middleware: List[BaseMiddleware] = []
        self._running = False
    
    def add_middleware(self, middleware: BaseMiddleware) -> None:
        """Add middleware to the execution pipeline."""
        self.middleware.append(middleware)
        self.logger.debug(f"Added middleware: {middleware.__class__.__name__}")
    
    async def execute_tool(
        self, 
        tool: BaseTool, 
        context: ExecutionContext,
        **kwargs
    ) -> ExecutionResult[ToolResult]:
        """Execute a single tool with middleware processing."""
        import time
        start_time = time.time()
        
        try:
            # Emit pre-execution event
            await self.event_bus.emit(Event(
                name="tool.execution.started",
                data={"tool_name": tool.name, "context": context}
            ))
            
            # Process through middleware chain
            async with self._middleware_context(tool, context) as processed_context:
                result = await self._execute_tool_internal(tool, processed_context, **kwargs)
            
            execution_time = time.time() - start_time
            execution_result = ExecutionResult(
                success=True,
                result=result,
                execution_time=execution_time
            )
            
            # Emit success event
            await self.event_bus.emit(Event(
                name="tool.execution.completed",
                data={"tool_name": tool.name, "result": execution_result}
            ))
            
            return execution_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            execution_result = ExecutionResult(
                success=False,
                error=e,
                execution_time=execution_time
            )
            
            self.logger.error(f"Tool execution failed: {tool.name}", exc_info=True)
            
            # Emit error event
            await self.event_bus.emit(Event(
                name="tool.execution.failed",
                data={"tool_name": tool.name, "error": str(e), "result": execution_result}
            ))
            
            return execution_result
    
    @asynccontextmanager
    async def _middleware_context(self, tool: BaseTool, context: ExecutionContext):
        """Process tool execution through middleware chain."""
        processed_context = context
        
        # Pre-processing through middleware
        for middleware in self.middleware:
            processed_context = await middleware.pre_process(tool, processed_context)
        
        try:
            yield processed_context
        finally:
            # Post-processing through middleware (in reverse order)
            for middleware in reversed(self.middleware):
                await middleware.post_process(tool, processed_context)
    
    @abstractmethod
    async def _execute_tool_internal(
        self, 
        tool: BaseTool, 
        context: ExecutionContext,
        **kwargs
    ) -> ToolResult:
        """Internal tool execution implementation."""
        pass
    
    @abstractmethod
    async def execute(
        self, 
        context: ExecutionContext,
        **kwargs
    ) -> ExecutionResult[Any]:
        """Execute the main workflow."""
        pass
    
    async def start(self) -> None:
        """Start the executor."""
        if self._running:
            return
        
        self._running = True
        self.logger.info(f"Starting executor: {self.__class__.__name__}")
        
        await self.event_bus.emit(Event(
            name="executor.started",
            data={"executor": self.__class__.__name__}
        ))
    
    async def stop(self) -> None:
        """Stop the executor gracefully."""
        if not self._running:
            return
        
        self._running = False
        self.logger.info(f"Stopping executor: {self.__class__.__name__}")
        
        await self.event_bus.emit(Event(
            name="executor.stopped",
            data={"executor": self.__class__.__name__}
        ))
    
    @property
    def is_running(self) -> bool:
        """Check if executor is running."""
        return self._running