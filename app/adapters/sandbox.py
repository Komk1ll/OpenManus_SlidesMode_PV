"""Sandbox client adapter for dependency injection."""

from typing import Any, Dict, Optional

from app.interfaces.sandbox import ISandboxClient
from app.sandbox.client import LocalSandboxClient
from app.config import SandboxSettings


class SandboxClientAdapter(ISandboxClient):
    """Adapter for LocalSandboxClient to implement ISandboxClient interface."""

    def __init__(self, client: Optional[LocalSandboxClient] = None):
        """Initialize the adapter.
        
        Args:
            client: Optional LocalSandboxClient instance. If None, creates a new one.
        """
        self._client = client or LocalSandboxClient()

    async def create(
        self,
        config: Optional[SandboxSettings] = None,
        volume_bindings: Optional[Dict[str, str]] = None,
    ) -> None:
        """Create sandbox.
        
        Args:
            config: Sandbox configuration.
            volume_bindings: Volume mappings.
        """
        await self._client.create(config, volume_bindings)

    async def run_command(self, command: str, timeout: Optional[int] = None) -> str:
        """Execute command in sandbox.
        
        Args:
            command: Command to execute.
            timeout: Execution timeout in seconds.
            
        Returns:
            Command output.
        """
        return await self._client.run_command(command, timeout)

    async def copy_from(self, container_path: str, local_path: str) -> None:
        """Copy file from container to local.
        
        Args:
            container_path: File path in container.
            local_path: Local destination path.
        """
        await self._client.copy_from(container_path, local_path)

    async def copy_to(self, local_path: str, container_path: str) -> None:
        """Copy file from local to container.
        
        Args:
            local_path: Local source file path.
            container_path: Destination path in container.
        """
        await self._client.copy_to(local_path, container_path)

    async def read_file(self, path: str) -> str:
        """Read file from container.
        
        Args:
            path: File path in container.
            
        Returns:
            File content.
        """
        return await self._client.read_file(path)

    async def write_file(self, path: str, content: str) -> None:
        """Write file to container.
        
        Args:
            path: File path in container.
            content: File content.
        """
        await self._client.write_file(path, content)

    async def cleanup(self) -> None:
        """Clean up resources."""
        await self._client.cleanup()

    async def health_check(self) -> bool:
        """Check if sandbox is healthy.
        
        Returns:
            True if sandbox is healthy, False otherwise.
        """
        try:
            # Simple health check by running a basic command
            if self._client.sandbox is None:
                return False
            await self._client.run_command("echo 'health_check'", timeout=5)
            return True
        except Exception:
            return False

    async def execute_command(
        self, 
        command: str, 
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a command in the sandbox.
        
        Args:
            command: Command to execute
            timeout: Execution timeout in seconds
            **kwargs: Additional execution parameters
            
        Returns:
            Execution result with stdout, stderr, exit_code
        """
        try:
            output = await self._client.run_command(command, timeout)
            return {
                "stdout": output,
                "stderr": "",
                "exit_code": "0"
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": "1"
            }

    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a file to the sandbox.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path in sandbox
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            await self._client.copy_to(local_path, remote_path)
            return True
        except Exception:
            return False

    async def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download a file from the sandbox.
        
        Args:
            remote_path: Remote file path in sandbox
            local_path: Local file path
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            await self._client.copy_from(remote_path, local_path)
            return True
        except Exception:
            return False

    async def is_healthy(self) -> bool:
        """Check if sandbox is healthy and responsive.
        
        Returns:
            True if sandbox is healthy, False otherwise
        """
        return await self.health_check()

    @property
    def sandbox_id(self) -> Optional[str]:
        """Get sandbox ID.
        
        Returns:
            Sandbox ID if available, None otherwise.
        """
        if self._client.sandbox and hasattr(self._client.sandbox, 'container_id'):
            return getattr(self._client.sandbox, 'container_id')
        return None