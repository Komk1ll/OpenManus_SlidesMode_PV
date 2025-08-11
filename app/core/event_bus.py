"""Event bus implementation for pub/sub communication.

Provides a centralized event system for decoupled communication
between different components of the presentation system.
"""

from typing import Any, Dict, List, Callable, Awaitable, Optional
from dataclasses import dataclass, field
import asyncio
import logging
from datetime import datetime
import weakref
from collections import defaultdict

@dataclass
class Event:
    """Event data structure."""
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Event name cannot be empty")

EventHandler = Callable[[Event], Awaitable[None]]

class EventBus:
    """Centralized event bus for pub/sub communication.
    
    Supports async event handlers, weak references to prevent memory leaks,
    and event filtering by name patterns.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._weak_handlers: Dict[str, List] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._running = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processor_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the event bus processor."""
        if self._running:
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())
        self.logger.info("Event bus started")
    
    async def stop(self) -> None:
        """Stop the event bus processor."""
        if not self._running:
            return
        
        self._running = False
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Event bus stopped")
    
    def subscribe(self, event_name: str, handler: EventHandler, weak: bool = False) -> None:
        """Subscribe to events by name.
        
        Args:
            event_name: Name of the event to subscribe to (supports wildcards)
            handler: Async function to handle the event
            weak: Use weak reference to prevent memory leaks
        """
        if weak:
            # Use weak reference to prevent memory leaks
            weak_handler = weakref.WeakMethod(handler) if hasattr(handler, '__self__') else weakref.ref(handler)
            self._weak_handlers[event_name].append(weak_handler)
        else:
            self._handlers[event_name].append(handler)
        
        self.logger.debug(f"Subscribed to event: {event_name} (weak: {weak})")
    
    def unsubscribe(self, event_name: str, handler: EventHandler) -> bool:
        """Unsubscribe from events.
        
        Args:
            event_name: Name of the event to unsubscribe from
            handler: Handler function to remove
            
        Returns:
            True if handler was found and removed
        """
        # Remove from regular handlers
        if handler in self._handlers[event_name]:
            self._handlers[event_name].remove(handler)
            self.logger.debug(f"Unsubscribed from event: {event_name}")
            return True
        
        # Remove from weak handlers
        for weak_handler in self._weak_handlers[event_name][:]:
            if weak_handler() == handler:
                self._weak_handlers[event_name].remove(weak_handler)
                self.logger.debug(f"Unsubscribed from event: {event_name} (weak)")
                return True
        
        return False
    
    async def emit(self, event: Event) -> None:
        """Emit an event to all subscribers.
        
        Args:
            event: Event to emit
        """
        if not self._running:
            await self.start()
        
        await self._event_queue.put(event)
        self.logger.debug(f"Event queued: {event.name}")
    
    async def emit_sync(self, event: Event) -> None:
        """Emit an event synchronously (wait for all handlers).
        
        Args:
            event: Event to emit
        """
        await self._process_event(event)
    
    async def _process_events(self) -> None:
        """Process events from the queue."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}", exc_info=True)
    
    async def _process_event(self, event: Event) -> None:
        """Process a single event."""
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Find matching handlers
        handlers = self._get_matching_handlers(event.name)
        
        if not handlers:
            self.logger.debug(f"No handlers for event: {event.name}")
            return
        
        # Execute handlers concurrently
        tasks = []
        for handler in handlers:
            task = asyncio.create_task(self._safe_execute_handler(handler, event))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            self.logger.debug(f"Event processed: {event.name} ({len(tasks)} handlers)")
    
    def _get_matching_handlers(self, event_name: str) -> List[EventHandler]:
        """Get all handlers that match the event name."""
        handlers = []
        
        # Exact match handlers
        handlers.extend(self._handlers.get(event_name, []))
        
        # Wildcard handlers
        for pattern in self._handlers:
            if self._matches_pattern(event_name, pattern):
                handlers.extend(self._handlers[pattern])
        
        # Weak reference handlers (clean up dead references)
        for pattern in list(self._weak_handlers.keys()):
            if self._matches_pattern(event_name, pattern):
                weak_handlers = self._weak_handlers[pattern]
                for weak_handler in weak_handlers[:]:
                    handler = weak_handler()
                    if handler is None:
                        # Dead reference, remove it
                        weak_handlers.remove(weak_handler)
                    else:
                        handlers.append(handler)
        
        return handlers
    
    def _matches_pattern(self, event_name: str, pattern: str) -> bool:
        """Check if event name matches pattern (supports * wildcard)."""
        if pattern == event_name:
            return True
        
        if '*' in pattern:
            import fnmatch
            return fnmatch.fnmatch(event_name, pattern)
        
        return False
    
    async def _safe_execute_handler(self, handler: EventHandler, event: Event) -> None:
        """Safely execute an event handler."""
        try:
            await handler(event)
        except Exception as e:
            self.logger.error(
                f"Error in event handler for {event.name}: {e}", 
                exc_info=True
            )
    
    def get_event_history(self, limit: Optional[int] = None) -> List[Event]:
        """Get event history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        if limit is None:
            return self._event_history.copy()
        return self._event_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
        self.logger.debug("Event history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        handler_counts = {}
        for event_name, handlers in self._handlers.items():
            handler_counts[event_name] = len(handlers)
        
        weak_handler_counts = {}
        for event_name, weak_handlers in self._weak_handlers.items():
            # Count only live weak references
            live_count = sum(1 for wh in weak_handlers if wh() is not None)
            if live_count > 0:
                weak_handler_counts[event_name] = live_count
        
        return {
            "running": self._running,
            "queue_size": self._event_queue.qsize(),
            "history_size": len(self._event_history),
            "handler_counts": handler_counts,
            "weak_handler_counts": weak_handler_counts
        }