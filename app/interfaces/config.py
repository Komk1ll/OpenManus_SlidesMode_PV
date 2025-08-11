"""Configuration Interface for dependency injection."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


class IConfig(ABC):
    """Interface for application configuration.
    
    Provides abstraction over different configuration sources.
    """

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        pass

    @abstractmethod
    def get_str(self, key: str, default: str = "") -> str:
        """Get a string configuration value.
        
        Args:
            key: Configuration key
            default: Default string value
            
        Returns:
            String configuration value
        """
        pass

    @abstractmethod
    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer configuration value.
        
        Args:
            key: Configuration key
            default: Default integer value
            
        Returns:
            Integer configuration value
        """
        pass

    @abstractmethod
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a float configuration value.
        
        Args:
            key: Configuration key
            default: Default float value
            
        Returns:
            Float configuration value
        """
        pass

    @abstractmethod
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value.
        
        Args:
            key: Configuration key
            default: Default boolean value
            
        Returns:
            Boolean configuration value
        """
        pass

    @abstractmethod
    def get_list(self, key: str, default: Optional[list] = None) -> list:
        """Get a list configuration value.
        
        Args:
            key: Configuration key
            default: Default list value
            
        Returns:
            List configuration value
        """
        pass

    @abstractmethod
    def get_dict(self, key: str, default: Optional[dict] = None) -> dict:
        """Get a dictionary configuration value.
        
        Args:
            key: Configuration key
            default: Default dictionary value
            
        Returns:
            Dictionary configuration value
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        """Check if a configuration key exists.
        
        Args:
            key: Configuration key
            
        Returns:
            True if key exists, False otherwise
        """
        pass

    @property
    @abstractmethod
    def workspace_root(self) -> str:
        """Get the workspace root directory."""
        pass

    @property
    @abstractmethod
    def log_level(self) -> str:
        """Get the logging level."""
        pass