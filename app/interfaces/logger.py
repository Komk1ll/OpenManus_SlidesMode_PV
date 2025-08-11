"""Logger Interface for dependency injection."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ILogger(ABC):
    """Interface for structured logging.
    
    Provides abstraction over different logging implementations.
    """

    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message.
        
        Args:
            message: The log message
            **kwargs: Additional structured data
        """
        pass

    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message.
        
        Args:
            message: The log message
            **kwargs: Additional structured data
        """
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message.
        
        Args:
            message: The log message
            **kwargs: Additional structured data
        """
        pass

    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message.
        
        Args:
            message: The log message
            **kwargs: Additional structured data
        """
        pass

    @abstractmethod
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message.
        
        Args:
            message: The log message
            **kwargs: Additional structured data
        """
        pass

    @abstractmethod
    def bind(self, **kwargs: Any) -> "ILogger":
        """Bind additional context to the logger.
        
        Args:
            **kwargs: Context data to bind
            
        Returns:
            A new logger instance with bound context
        """
        pass

    @abstractmethod
    def with_correlation_id(self, correlation_id: str) -> "ILogger":
        """Create a logger with correlation ID for request tracing.
        
        Args:
            correlation_id: Unique identifier for request correlation
            
        Returns:
            A new logger instance with correlation ID
        """
        pass