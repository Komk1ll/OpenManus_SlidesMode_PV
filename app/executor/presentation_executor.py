"""Presentation executor for orchestrating tool execution.

Provides centralized execution management with middleware support,
error handling, streaming, and event-driven architecture.
"""

from typing import Any, Dict, List, Optional, AsyncIterator, Union, Callable
from dataclasses import dataclass, field
import asyncio
import logging
from datetime import datetime
from enum import Enum
import uuid
import traceback
from contextlib import asynccontextmanager

from ..core.base_executor import BaseExecutor, ExecutionContext, ExecutionResult
from ..core.base_middleware import BaseMiddleware
from ..core.event_bus import EventBus, Event
from ..core.config_manager import ConfigManager
from ..core.tool_registry import ToolRegistry, BaseTool

class ExecutionMode(Enum):
    """Execution modes for the presentation executor."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    STREAMING = "streaming"

@dataclass
class PresentationRequest:
    """Request for presentation generation."""
    topic: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    tools: List[str] = field(default_factory=list)
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    streaming: bool = False
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class PresentationResponse:
    """Response from presentation generation."""
    request_id: str
    success: bool
    content: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    tool_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StreamingChunk:
    """Streaming response chunk."""
    request_id: str
    chunk_id: str
    tool_name: str
    content: Any
    is_final: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

class PresentationExecutor(BaseExecutor):
    """Main executor for presentation generation.
    
    Orchestrates tool execution with support for different execution modes,
    middleware processing, event handling, and streaming responses.
    """
    
    def __init__(self, 
                 tool_registry: ToolRegistry,
                 config_manager: ConfigManager,
                 event_bus: EventBus,
                 middleware: Optional[List[BaseMiddleware]] = None):
        super().__init__()
        self.tool_registry = tool_registry
        self.config_manager = config_manager
        self.event_bus = event_bus
        self.middleware_chain = middleware or []
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Execution state
        self._active_executions: Dict[str, asyncio.Task] = {}
        self._execution_history: List[ExecutionResult] = []
        self._max_history = 1000
        
        # Performance metrics
        self._metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0
        }
    
    async def initialize(self) -> None:
        """Initialize the executor."""
        await super().initialize()
        
        # Subscribe to events
        await self.event_bus.subscribe("tool.error", self._handle_tool_error)
        await self.event_bus.subscribe("execution.timeout", self._handle_execution_timeout)
        
        self.logger.info("Presentation executor initialized")
    
    async def dispose(self) -> None:
        """Dispose of the executor."""
        # Cancel active executions
        for execution_id, task in self._active_executions.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self._active_executions.clear()
        await super().dispose()
        self.logger.info("Presentation executor disposed")
    
    async def execute_presentation(self, request: PresentationRequest) -> PresentationResponse:
        """Execute a presentation generation request.
        
        Args:
            request: Presentation request
            
        Returns:
            Presentation response
        """
        start_time = datetime.now()
        request_id = request.correlation_id
        
        # Create execution context
        context = ExecutionContext(
            request_id=request_id,
            data={"request": request},
            metadata=request.metadata.copy()
        )
        
        try:
            # Emit start event
            await self.event_bus.emit(Event(
                name="presentation.execution.started",
                data={"request_id": request_id, "topic": request.topic},
                correlation_id=request_id
            ))
            
            # Execute based on mode
            if request.streaming:
                # For streaming, we need to handle it differently
                response = await self._execute_streaming(request, context)
            else:
                response = await self._execute_standard(request, context)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            response.execution_time = execution_time
            
            # Update metrics
            self._update_metrics(True, execution_time)
            
            # Emit completion event
            await self.event_bus.emit(Event(
                name="presentation.execution.completed",
                data={
                    "request_id": request_id,
                    "success": response.success,
                    "execution_time": execution_time
                },
                correlation_id=request_id
            ))
            
            return response
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(False, execution_time)
            
            # Create error response
            response = PresentationResponse(
                request_id=request_id,
                success=False,
                execution_time=execution_time,
                errors=[str(e)]
            )
            
            # Emit error event
            await self.event_bus.emit(Event(
                name="presentation.execution.failed",
                data={
                    "request_id": request_id,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                },
                correlation_id=request_id
            ))
            
            self.logger.error(f"Presentation execution failed: {e}", exc_info=True)
            return response
    
    async def _execute_standard(self, 
                              request: PresentationRequest, 
                              context: ExecutionContext) -> PresentationResponse:
        """Execute standard (non-streaming) presentation generation."""
        response = PresentationResponse(
            request_id=request.correlation_id,
            success=True
        )
        
        # Determine tools to execute
        tools_to_execute = request.tools or self._get_default_tools(request)
        
        # Execute based on mode
        if request.mode == ExecutionMode.SEQUENTIAL:
            await self._execute_sequential(tools_to_execute, request, context, response)
        elif request.mode == ExecutionMode.PARALLEL:
            await self._execute_parallel(tools_to_execute, request, context, response)
        elif request.mode == ExecutionMode.PIPELINE:
            await self._execute_pipeline(tools_to_execute, request, context, response)
        else:
            raise ValueError(f"Unsupported execution mode: {request.mode}")
        
        return response
    
    async def _execute_streaming(self, 
                               request: PresentationRequest, 
                               context: ExecutionContext) -> PresentationResponse:
        """Execute streaming presentation generation."""
        # For streaming, we create a task and return immediately
        # The actual streaming happens through async iteration
        response = PresentationResponse(
            request_id=request.correlation_id,
            success=True,
            metadata={"streaming": True}
        )
        
        return response
    
    async def stream_presentation(self, request: PresentationRequest) -> AsyncIterator[StreamingChunk]:
        """Stream presentation generation results.
        
        Args:
            request: Presentation request
            
        Yields:
            Streaming chunks
        """
        request_id = request.correlation_id
        tools_to_execute = request.tools or self._get_default_tools(request)
        
        context = ExecutionContext(
            request_id=request_id,
            data={"request": request},
            metadata=request.metadata.copy()
        )
        
        try:
            for i, tool_name in enumerate(tools_to_execute):
                # Get tool instance
                tool = await self.tool_registry.get_tool(tool_name)
                
                # Execute tool with streaming
                async for chunk in self._execute_tool_streaming(tool, request, context):
                    yield StreamingChunk(
                        request_id=request_id,
                        chunk_id=str(uuid.uuid4()),
                        tool_name=tool_name,
                        content=chunk,
                        is_final=(i == len(tools_to_execute) - 1)
                    )
        
        except Exception as e:
            # Yield error chunk
            yield StreamingChunk(
                request_id=request_id,
                chunk_id=str(uuid.uuid4()),
                tool_name="error",
                content={"error": str(e)},
                is_final=True
            )
    
    async def _execute_sequential(self, 
                                tools: List[str], 
                                request: PresentationRequest,
                                context: ExecutionContext,
                                response: PresentationResponse) -> None:
        """Execute tools sequentially."""
        for tool_name in tools:
            try:
                tool = await self.tool_registry.get_tool(tool_name)
                result = await self._execute_single_tool(tool, request, context)
                response.tool_results[tool_name] = result
                
                # Update context with result for next tool
                context.data[f"{tool_name}_result"] = result
                
            except Exception as e:
                response.errors.append(f"Tool {tool_name}: {str(e)}")
                response.success = False
                self.logger.error(f"Error executing tool {tool_name}: {e}")
    
    async def _execute_parallel(self, 
                              tools: List[str], 
                              request: PresentationRequest,
                              context: ExecutionContext,
                              response: PresentationResponse) -> None:
        """Execute tools in parallel."""
        tasks = []
        
        for tool_name in tools:
            task = asyncio.create_task(
                self._execute_tool_with_error_handling(tool_name, request, context)
            )
            tasks.append((tool_name, task))
        
        # Wait for all tasks to complete
        for tool_name, task in tasks:
            try:
                result = await task
                response.tool_results[tool_name] = result
            except Exception as e:
                response.errors.append(f"Tool {tool_name}: {str(e)}")
                response.success = False
    
    async def _execute_pipeline(self, 
                              tools: List[str], 
                              request: PresentationRequest,
                              context: ExecutionContext,
                              response: PresentationResponse) -> None:
        """Execute tools in pipeline mode (output of one feeds into next)."""
        pipeline_data = request.requirements.copy()
        
        for tool_name in tools:
            try:
                tool = await self.tool_registry.get_tool(tool_name)
                
                # Create context with pipeline data
                tool_context = ExecutionContext(
                    request_id=context.request_id,
                    data={**context.data, "pipeline_input": pipeline_data},
                    metadata=context.metadata
                )
                
                result = await self._execute_single_tool(tool, request, tool_context)
                response.tool_results[tool_name] = result
                
                # Update pipeline data for next tool
                if isinstance(result, dict):
                    pipeline_data.update(result)
                else:
                    pipeline_data[tool_name] = result
                
            except Exception as e:
                response.errors.append(f"Tool {tool_name}: {str(e)}")
                response.success = False
                break  # Stop pipeline on error
    
    async def _execute_tool_with_error_handling(self, 
                                              tool_name: str, 
                                              request: PresentationRequest,
                                              context: ExecutionContext) -> Any:
        """Execute a single tool with error handling."""
        try:
            tool = await self.tool_registry.get_tool(tool_name)
            return await self._execute_single_tool(tool, request, context)
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    async def _execute_single_tool(self, 
                                 tool: BaseTool, 
                                 request: PresentationRequest,
                                 context: ExecutionContext) -> Any:
        """Execute a single tool with middleware processing."""
        # Apply pre-execution middleware
        for middleware in self.middleware_chain:
            await middleware.before_execution(context)
        
        try:
            # Execute tool
            if hasattr(tool, 'execute_async'):
                result = await tool.execute_async(request.topic, request.requirements)
            elif hasattr(tool, 'execute'):
                result = tool.execute(request.topic, request.requirements)
            else:
                raise AttributeError(f"Tool {tool.name} has no execute method")
            
            # Apply post-execution middleware
            for middleware in self.middleware_chain:
                await middleware.after_execution(context, result)
            
            return result
            
        except Exception as e:
            # Apply error middleware
            for middleware in self.middleware_chain:
                await middleware.on_error(context, e)
            raise
    
    async def _execute_tool_streaming(self, 
                                    tool: BaseTool, 
                                    request: PresentationRequest,
                                    context: ExecutionContext) -> AsyncIterator[Any]:
        """Execute a tool with streaming output."""
        if hasattr(tool, 'execute_streaming'):
            async for chunk in tool.execute_streaming(request.topic, request.requirements):
                yield chunk
        else:
            # Fallback to regular execution
            result = await self._execute_single_tool(tool, request, context)
            yield result
    
    def _get_default_tools(self, request: PresentationRequest) -> List[str]:
        """Get default tools for presentation generation."""
        # This could be configurable or based on request analysis
        default_tools = self.config_manager.get('presentation.default_tools', [
            'content_generator',
            'slide_creator',
            'formatter'
        ])
        
        return default_tools
    
    async def _handle_tool_error(self, event: Event) -> None:
        """Handle tool error events."""
        self.logger.warning(f"Tool error: {event.data}")
    
    async def _handle_execution_timeout(self, event: Event) -> None:
        """Handle execution timeout events."""
        request_id = event.data.get('request_id')
        if request_id in self._active_executions:
            task = self._active_executions[request_id]
            if not task.done():
                task.cancel()
                self.logger.warning(f"Execution {request_id} timed out and was cancelled")
    
    def _update_metrics(self, success: bool, execution_time: float) -> None:
        """Update execution metrics."""
        self._metrics["total_executions"] += 1
        
        if success:
            self._metrics["successful_executions"] += 1
        else:
            self._metrics["failed_executions"] += 1
        
        # Update average execution time
        total = self._metrics["total_executions"]
        current_avg = self._metrics["average_execution_time"]
        self._metrics["average_execution_time"] = (
            (current_avg * (total - 1) + execution_time) / total
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        return self._metrics.copy()
    
    def get_active_executions(self) -> List[str]:
        """Get list of active execution IDs."""
        return list(self._active_executions.keys())
    
    async def cancel_execution(self, request_id: str) -> bool:
        """Cancel an active execution.
        
        Args:
            request_id: Request ID to cancel
            
        Returns:
            True if execution was cancelled
        """
        if request_id in self._active_executions:
            task = self._active_executions[request_id]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                del self._active_executions[request_id]
                self.logger.info(f"Execution {request_id} cancelled")
                return True
        
        return False
    
    @asynccontextmanager
    async def execution_context(self, request: PresentationRequest):
        """Context manager for execution lifecycle."""
        request_id = request.correlation_id
        
        try:
            # Register execution
            task = asyncio.current_task()
            if task:
                self._active_executions[request_id] = task
            
            yield request_id
            
        finally:
            # Cleanup
            if request_id in self._active_executions:
                del self._active_executions[request_id]