"""Structured Logger Adapter implementing ILogger interface."""

import uuid
from typing import Any

import structlog
from structlog.stdlib import LoggerFactory

from app.interfaces.logger import ILogger


class StructuredLogger(ILogger):
    """Structured logger implementation using structlog.
    
    Provides structured logging with correlation IDs and context binding.
    """

    def __init__(self, level: str = "INFO", correlation_id: str = ""):
        """Initialize the structured logger.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            correlation_id: Optional correlation ID for request tracing
        """
        # Configure structlog if not already configured
        if not structlog.is_configured():
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
        
        self._logger = structlog.get_logger("spark")
        self._context = {}
        
        if correlation_id:
            self._context["correlation_id"] = correlation_id
        
        # Set log level
        import logging
        logging.getLogger().setLevel(getattr(logging, level.upper(), logging.INFO))

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self._logger.debug(message, **self._context, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self._logger.info(message, **self._context, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self._logger.warning(message, **self._context, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        self._logger.error(message, **self._context, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message."""
        self._logger.critical(message, **self._context, **kwargs)

    def bind(self, **kwargs: Any) -> "StructuredLogger":
        """Bind additional context to the logger."""
        new_logger = StructuredLogger()
        new_logger._logger = self._logger
        new_logger._context = {**self._context, **kwargs}
        return new_logger

    def with_correlation_id(self, correlation_id: str) -> "StructuredLogger":
        """Create a logger with correlation ID for request tracing."""
        return self.bind(correlation_id=correlation_id)

    @classmethod
    def create_with_correlation_id(cls, level: str = "INFO") -> "StructuredLogger":
        """Create a logger with auto-generated correlation ID."""
        correlation_id = str(uuid.uuid4())
        return cls(level=level, correlation_id=correlation_id)