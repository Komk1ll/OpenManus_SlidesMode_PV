"""Base middleware class for tool execution pipeline.

Provides the foundation for implementing middleware that can process
tool execution requests before and after execution.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

from ..tool.base import BaseTool
from .base_executor import ExecutionContext

class BaseMiddleware(ABC):
    """Base class for execution middleware.
    
    Middleware can intercept and modify tool execution flow,
    providing cross-cutting concerns like logging, caching,
    authentication, and metrics collection.
    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"middleware.{self.name}")
        self.enabled = True
    
    async def pre_process(
        self, 
        tool: BaseTool, 
        context: ExecutionContext
    ) -> ExecutionContext:
        """Process tool execution before it runs.
        
        Args:
            tool: The tool about to be executed
            context: Current execution context
            
        Returns:
            Modified execution context
        """
        if not self.enabled:
            return context
        
        try:
            return await self._pre_process_internal(tool, context)
        except Exception as e:
            self.logger.error(f"Pre-processing failed in {self.name}", exc_info=True)
            # Continue execution even if middleware fails
            return context
    
    async def post_process(
        self, 
        tool: BaseTool, 
        context: ExecutionContext
    ) -> None:
        """Process tool execution after it completes.
        
        Args:
            tool: The tool that was executed
            context: Current execution context
        """
        if not self.enabled:
            return
        
        try:
            await self._post_process_internal(tool, context)
        except Exception as e:
            self.logger.error(f"Post-processing failed in {self.name}", exc_info=True)
            # Don't propagate middleware errors
    
    @abstractmethod
    async def _pre_process_internal(
        self, 
        tool: BaseTool, 
        context: ExecutionContext
    ) -> ExecutionContext:
        """Internal pre-processing implementation."""
        pass
    
    @abstractmethod
    async def _post_process_internal(
        self, 
        tool: BaseTool, 
        context: ExecutionContext
    ) -> None:
        """Internal post-processing implementation."""
        pass
    
    def enable(self) -> None:
        """Enable this middleware."""
        self.enabled = True
        self.logger.debug(f"Middleware {self.name} enabled")
    
    def disable(self) -> None:
        """Disable this middleware."""
        self.enabled = False
        self.logger.debug(f"Middleware {self.name} disabled")
    
    def __repr__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"{self.__class__.__name__}(name='{self.name}', {status})"

class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging tool execution."""
    
    def __init__(self, log_level: str = "INFO"):
        super().__init__("logging")
        self.log_level = getattr(logging, log_level.upper())
    
    async def _pre_process_internal(
        self, 
        tool: BaseTool, 
        context: ExecutionContext
    ) -> ExecutionContext:
        self.logger.log(
            self.log_level,
            f"Executing tool: {tool.name} (session: {context.session_id})"
        )
        return context
    
    async def _post_process_internal(
        self, 
        tool: BaseTool, 
        context: ExecutionContext
    ) -> None:
        self.logger.log(
            self.log_level,
            f"Completed tool: {tool.name} (session: {context.session_id})"
        )

class MetricsMiddleware(BaseMiddleware):
    """Middleware for collecting execution metrics."""
    
    def __init__(self):
        super().__init__("metrics")
        self.execution_counts: Dict[str, int] = {}
        self.execution_times: Dict[str, float] = {}
    
    async def _pre_process_internal(
        self, 
        tool: BaseTool, 
        context: ExecutionContext
    ) -> ExecutionContext:
        import time
        context.metadata["start_time"] = time.time()
        return context
    
    async def _post_process_internal(
        self, 
        tool: BaseTool, 
        context: ExecutionContext
    ) -> None:
        import time
        start_time = context.metadata.get("start_time")
        if start_time:
            execution_time = time.time() - start_time
            
            # Update metrics
            self.execution_counts[tool.name] = self.execution_counts.get(tool.name, 0) + 1
            self.execution_times[tool.name] = execution_time
            
            self.logger.debug(
                f"Tool {tool.name} executed in {execution_time:.3f}s "
                f"(total executions: {self.execution_counts[tool.name]})"
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return {
            "execution_counts": self.execution_counts.copy(),
            "execution_times": self.execution_times.copy()
        }
    
    def reset_metrics(self) -> None:
        """Reset all collected metrics."""
        self.execution_counts.clear()
        self.execution_times.clear()
        self.logger.info("Metrics reset")