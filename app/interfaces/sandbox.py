"""Sandbox Client Interface for dependency injection."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ISandboxClient(ABC):
    """Interface for sandbox client operations.
    
    Provides abstraction over different sandbox implementations.
    """

    @abstractmethod
    async def execute_command(
        self, 
        command: str, 
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute a command in the sandbox.
        
        Args:
            command: Command to execute
            timeout: Execution timeout in seconds
            **kwargs: Additional execution parameters
            
        Returns:
            Execution result with stdout, stderr, exit_code
        """
        pass

    @abstractmethod
    async def upload_file(
        self, 
        local_path: str, 
        remote_path: str
    ) -> bool:
        """Upload a file to the sandbox.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path in sandbox
            
        Returns:
            True if upload successful, False otherwise
        """
        pass

    @abstractmethod
    async def download_file(
        self, 
        remote_path: str, 
        local_path: str
    ) -> bool:
        """Download a file from the sandbox.
        
        Args:
            remote_path: Remote file path in sandbox
            local_path: Local file path
            
        Returns:
            True if download successful, False otherwise
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up sandbox resources."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if sandbox is healthy and responsive.
        
        Returns:
            True if sandbox is healthy, False otherwise
        """
        pass

    @property
    @abstractmethod
    def sandbox_id(self) -> Optional[str]:
        """Get the sandbox identifier."""
        pass