"""Core middleware implementations for presentation execution.

Provides essential middleware for logging, metrics, authentication,
validation, caching, and error handling.
"""

from typing import Any, Dict, Optional, List
import time
import logging
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import hashlib
import asyncio
from contextlib import asynccontextmanager

from ..core.base_middleware import BaseMiddleware
from ..core.base_executor import ExecutionContext
from ..core.event_bus import EventBus, Event

@dataclass
class MetricData:
    """Metric data structure."""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class EnhancedLoggingMiddleware(BaseMiddleware):
    """Enhanced logging middleware with structured logging and correlation IDs."""
    
    def __init__(self, 
                 logger: Optional[logging.Logger] = None,
                 log_level: int = logging.INFO,
                 include_context: bool = True,
                 include_performance: bool = True):
        super().__init__()
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.log_level = log_level
        self.include_context = include_context
        self.include_performance = include_performance
        self._start_times: Dict[str, float] = {}
    
    async def before_execution(self, context: ExecutionContext) -> None:
        """Log before execution."""
        self._start_times[context.request_id] = time.time()
        
        log_data = {
            "event": "execution_started",
            "request_id": context.request_id,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.include_context:
            log_data["context"] = {
                "metadata": context.metadata,
                "data_keys": list(context.data.keys()) if context.data else []
            }
        
        self.logger.log(self.log_level, json.dumps(log_data))
    
    async def after_execution(self, context: ExecutionContext, result: Any) -> None:
        """Log after successful execution."""
        execution_time = None
        if context.request_id in self._start_times:
            execution_time = time.time() - self._start_times[context.request_id]
            del self._start_times[context.request_id]
        
        log_data = {
            "event": "execution_completed",
            "request_id": context.request_id,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
        if self.include_performance and execution_time is not None:
            log_data["execution_time"] = execution_time
        
        if self.include_context:
            log_data["result_type"] = type(result).__name__
            if hasattr(result, '__len__'):
                try:
                    log_data["result_size"] = len(result)
                except TypeError:
                    pass
        
        self.logger.log(self.log_level, json.dumps(log_data))
    
    async def on_error(self, context: ExecutionContext, error: Exception) -> None:
        """Log execution errors."""
        execution_time = None
        if context.request_id in self._start_times:
            execution_time = time.time() - self._start_times[context.request_id]
            del self._start_times[context.request_id]
        
        log_data = {
            "event": "execution_failed",
            "request_id": context.request_id,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": {
                "type": type(error).__name__,
                "message": str(error)
            }
        }
        
        if self.include_performance and execution_time is not None:
            log_data["execution_time"] = execution_time
        
        self.logger.error(json.dumps(log_data))

class MetricsMiddleware(BaseMiddleware):
    """Middleware for collecting execution metrics."""
    
    def __init__(self, 
                 event_bus: Optional[EventBus] = None,
                 collect_detailed_metrics: bool = True):
        super().__init__()
        self.event_bus = event_bus
        self.collect_detailed_metrics = collect_detailed_metrics
        self._start_times: Dict[str, float] = {}
        self._metrics_buffer: List[MetricData] = []
        self._buffer_size = 1000
    
    async def before_execution(self, context: ExecutionContext) -> None:
        """Record execution start time."""
        self._start_times[context.request_id] = time.time()
        
        # Emit metric event
        if self.event_bus:
            await self.event_bus.emit(Event(
                name="metrics.execution.started",
                data={"request_id": context.request_id},
                correlation_id=context.request_id
            ))
    
    async def after_execution(self, context: ExecutionContext, result: Any) -> None:
        """Collect success metrics."""
        execution_time = self._get_execution_time(context.request_id)
        
        # Basic metrics
        await self._record_metric("execution.count", 1, {
            "status": "success",
            "request_id": context.request_id
        })
        
        if execution_time is not None:
            await self._record_metric("execution.duration", execution_time, {
                "status": "success",
                "request_id": context.request_id
            })
        
        # Detailed metrics
        if self.collect_detailed_metrics:
            await self._collect_detailed_metrics(context, result, execution_time)
    
    async def on_error(self, context: ExecutionContext, error: Exception) -> None:
        """Collect error metrics."""
        execution_time = self._get_execution_time(context.request_id)
        
        await self._record_metric("execution.count", 1, {
            "status": "error",
            "error_type": type(error).__name__,
            "request_id": context.request_id
        })
        
        if execution_time is not None:
            await self._record_metric("execution.duration", execution_time, {
                "status": "error",
                "error_type": type(error).__name__,
                "request_id": context.request_id
            })
    
    def _get_execution_time(self, request_id: str) -> Optional[float]:
        """Get execution time for request."""
        if request_id in self._start_times:
            execution_time = time.time() - self._start_times[request_id]
            del self._start_times[request_id]
            return execution_time
        return None
    
    async def _record_metric(self, name: str, value: float, tags: Dict[str, str]) -> None:
        """Record a metric."""
        metric = MetricData(name=name, value=value, tags=tags)
        self._metrics_buffer.append(metric)
        
        # Flush buffer if full
        if len(self._metrics_buffer) >= self._buffer_size:
            await self._flush_metrics()
        
        # Emit metric event
        if self.event_bus:
            await self.event_bus.emit(Event(
                name="metrics.recorded",
                data={"metric": metric.__dict__}
            ))
    
    async def _collect_detailed_metrics(self, 
                                      context: ExecutionContext, 
                                      result: Any, 
                                      execution_time: Optional[float]) -> None:
        """Collect detailed execution metrics."""
        tags = {"request_id": context.request_id}
        
        # Memory usage (if available)
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            await self._record_metric("execution.memory.rss", memory_info.rss, tags)
            await self._record_metric("execution.memory.vms", memory_info.vms, tags)
        except ImportError:
            pass
        
        # Result size metrics
        if hasattr(result, '__len__'):
            try:
                await self._record_metric("execution.result.size", len(result), tags)
            except TypeError:
                pass
        
        # Context data metrics
        if context.data:
            await self._record_metric("execution.context.data_keys", len(context.data), tags)
    
    async def _flush_metrics(self) -> None:
        """Flush metrics buffer."""
        if self.event_bus and self._metrics_buffer:
            await self.event_bus.emit(Event(
                name="metrics.batch",
                data={"metrics": [m.__dict__ for m in self._metrics_buffer]}
            ))
        
        self._metrics_buffer.clear()
    
    def get_buffered_metrics(self) -> List[MetricData]:
        """Get current buffered metrics."""
        return self._metrics_buffer.copy()

class ValidationMiddleware(BaseMiddleware):
    """Middleware for input and output validation."""
    
    def __init__(self, 
                 validate_input: bool = True,
                 validate_output: bool = True,
                 strict_mode: bool = False):
        super().__init__()
        self.validate_input = validate_input
        self.validate_output = validate_output
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def before_execution(self, context: ExecutionContext) -> None:
        """Validate input before execution."""
        if not self.validate_input:
            return
        
        validation_errors = []
        
        # Validate context structure
        if not context.request_id:
            validation_errors.append("Missing request_id in context")
        
        if not isinstance(context.data, dict):
            validation_errors.append("Context data must be a dictionary")
        
        if not isinstance(context.metadata, dict):
            validation_errors.append("Context metadata must be a dictionary")
        
        # Custom validation rules
        validation_errors.extend(await self._validate_context_data(context))
        
        if validation_errors:
            error_msg = f"Input validation failed: {'; '.join(validation_errors)}"
            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                self.logger.warning(error_msg)
    
    async def after_execution(self, context: ExecutionContext, result: Any) -> None:
        """Validate output after execution."""
        if not self.validate_output:
            return
        
        validation_errors = []
        
        # Basic result validation
        if result is None:
            validation_errors.append("Result is None")
        
        # Custom validation rules
        validation_errors.extend(await self._validate_result(result, context))
        
        if validation_errors:
            error_msg = f"Output validation failed: {'; '.join(validation_errors)}"
            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                self.logger.warning(error_msg)
    
    async def _validate_context_data(self, context: ExecutionContext) -> List[str]:
        """Validate context data. Override in subclasses."""
        errors = []
        
        # Example validations
        if 'request' in context.data:
            request = context.data['request']
            if hasattr(request, 'topic') and not request.topic:
                errors.append("Request topic is empty")
        
        return errors
    
    async def _validate_result(self, result: Any, context: ExecutionContext) -> List[str]:
        """Validate execution result. Override in subclasses."""
        errors = []
        
        # Example validations
        if isinstance(result, dict):
            if 'error' in result and result['error']:
                errors.append(f"Result contains error: {result['error']}")
        
        return errors

class CachingMiddleware(BaseMiddleware):
    """Middleware for caching execution results."""
    
    def __init__(self, 
                 cache_ttl: int = 3600,  # 1 hour
                 max_cache_size: int = 1000,
                 cache_key_generator: Optional[callable] = None):
        super().__init__()
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        self.cache_key_generator = cache_key_generator or self._default_cache_key
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, datetime] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def before_execution(self, context: ExecutionContext) -> None:
        """Check cache before execution."""
        cache_key = await self._generate_cache_key(context)
        
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            
            # Check if cache entry is still valid
            if self._is_cache_valid(cache_entry):
                # Update access time
                self._access_times[cache_key] = datetime.now()
                
                # Store cached result in context for retrieval
                context.metadata['_cached_result'] = cache_entry['result']
                context.metadata['_cache_hit'] = True
                
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return
        
        context.metadata['_cache_hit'] = False
        context.metadata['_cache_key'] = cache_key
    
    async def after_execution(self, context: ExecutionContext, result: Any) -> None:
        """Cache result after execution."""
        # Don't cache if we had a cache hit
        if context.metadata.get('_cache_hit', False):
            return
        
        cache_key = context.metadata.get('_cache_key')
        if not cache_key:
            return
        
        # Store in cache
        cache_entry = {
            'result': result,
            'timestamp': datetime.now(),
            'ttl': self.cache_ttl
        }
        
        self._cache[cache_key] = cache_entry
        self._access_times[cache_key] = datetime.now()
        
        # Cleanup old entries if cache is full
        await self._cleanup_cache()
        
        self.logger.debug(f"Cached result for key: {cache_key}")
    
    def _default_cache_key(self, context: ExecutionContext) -> str:
        """Generate default cache key from context."""
        # Create hash from context data (excluding metadata)
        data_str = json.dumps(context.data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def _generate_cache_key(self, context: ExecutionContext) -> str:
        """Generate cache key for context."""
        if asyncio.iscoroutinefunction(self.cache_key_generator):
            return await self.cache_key_generator(context)
        else:
            return self.cache_key_generator(context)
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        timestamp = cache_entry['timestamp']
        ttl = cache_entry['ttl']
        
        return datetime.now() - timestamp < timedelta(seconds=ttl)
    
    async def _cleanup_cache(self) -> None:
        """Clean up old cache entries."""
        if len(self._cache) <= self.max_cache_size:
            return
        
        # Remove expired entries first
        expired_keys = [
            key for key, entry in self._cache.items()
            if not self._is_cache_valid(entry)
        ]
        
        for key in expired_keys:
            del self._cache[key]
            if key in self._access_times:
                del self._access_times[key]
        
        # If still over limit, remove least recently accessed
        if len(self._cache) > self.max_cache_size:
            # Sort by access time
            sorted_keys = sorted(
                self._access_times.keys(),
                key=lambda k: self._access_times[k]
            )
            
            # Remove oldest entries
            keys_to_remove = sorted_keys[:len(self._cache) - self.max_cache_size]
            for key in keys_to_remove:
                if key in self._cache:
                    del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        valid_entries = sum(
            1 for entry in self._cache.values()
            if self._is_cache_valid(entry)
        )
        
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self._cache) - valid_entries,
            'max_size': self.max_cache_size,
            'ttl': self.cache_ttl
        }
    
    def clear_cache(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_times.clear()
        self.logger.info("Cache cleared")

class CircuitBreakerMiddleware(BaseMiddleware):
    """Circuit breaker middleware for handling external service failures."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        super().__init__()
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._state = "closed"  # closed, open, half-open
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def before_execution(self, context: ExecutionContext) -> None:
        """Check circuit breaker state before execution."""
        if self._state == "open":
            # Check if we should try to recover
            if (self._last_failure_time and 
                datetime.now() - self._last_failure_time > timedelta(seconds=self.recovery_timeout)):
                self._state = "half-open"
                self.logger.info("Circuit breaker moving to half-open state")
            else:
                raise Exception("Circuit breaker is open - execution blocked")
    
    async def after_execution(self, context: ExecutionContext, result: Any) -> None:
        """Handle successful execution."""
        if self._state == "half-open":
            # Success in half-open state - close the circuit
            self._state = "closed"
            self._failure_count = 0
            self._last_failure_time = None
            self.logger.info("Circuit breaker closed after successful execution")
    
    async def on_error(self, context: ExecutionContext, error: Exception) -> None:
        """Handle execution error."""
        if isinstance(error, self.expected_exception):
            self._failure_count += 1
            self._last_failure_time = datetime.now()
            
            if self._failure_count >= self.failure_threshold:
                self._state = "open"
                self.logger.warning(
                    f"Circuit breaker opened after {self._failure_count} failures"
                )
            elif self._state == "half-open":
                # Failure in half-open state - back to open
                self._state = "open"
                self.logger.warning("Circuit breaker back to open state after failure")
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            'state': self._state,
            'failure_count': self._failure_count,
            'failure_threshold': self.failure_threshold,
            'last_failure_time': self._last_failure_time.isoformat() if self._last_failure_time else None,
            'recovery_timeout': self.recovery_timeout
        }
    
    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        self._state = "closed"
        self._failure_count = 0
        self._last_failure_time = None
        self.logger.info("Circuit breaker manually reset")