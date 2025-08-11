"""Tool registry for dependency injection and lazy loading.

Provides centralized tool management with support for dependency injection,
lazy loading, lifecycle management, and tool discovery.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Callable, Union, Set
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import asyncio
import logging
import inspect
from datetime import datetime
from enum import Enum
import weakref
from pathlib import Path
import importlib
import importlib.util

T = TypeVar('T')

class ToolLifecycle(Enum):
    """Tool lifecycle states."""
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DISPOSED = "disposed"

@dataclass
class ToolMetadata:
    """Tool metadata and configuration."""
    name: str
    tool_class: Type
    dependencies: List[str] = field(default_factory=list)
    singleton: bool = True
    lazy: bool = True
    priority: int = 0
    tags: Set[str] = field(default_factory=set)
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    lifecycle: ToolLifecycle = ToolLifecycle.REGISTERED
    
class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{name}]")
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the tool."""
        if self._initialized:
            return
        
        await self._initialize()
        self._initialized = True
        self.logger.debug(f"Tool {self.name} initialized")
    
    async def dispose(self) -> None:
        """Dispose of the tool and clean up resources."""
        if not self._initialized:
            return
        
        await self._dispose()
        self._initialized = False
        self.logger.debug(f"Tool {self.name} disposed")
    
    @abstractmethod
    async def _initialize(self) -> None:
        """Tool-specific initialization logic."""
        pass
    
    async def _dispose(self) -> None:
        """Tool-specific disposal logic."""
        pass
    
    @property
    def is_initialized(self) -> bool:
        """Check if tool is initialized."""
        return self._initialized
    
    def get_dependencies(self) -> List[str]:
        """Get list of tool dependencies."""
        return getattr(self.__class__, '_dependencies', [])
    
    @classmethod
    def register_dependency(cls, dependency: str) -> None:
        """Register a dependency for this tool class."""
        if not hasattr(cls, '_dependencies'):
            cls._dependencies = []
        if dependency not in cls._dependencies:
            cls._dependencies.append(dependency)

class ToolFactory:
    """Factory for creating tool instances."""
    
    def __init__(self, tool_class: Type[BaseTool], metadata: ToolMetadata):
        self.tool_class = tool_class
        self.metadata = metadata
        self.logger = logging.getLogger(self.__class__.__name__)
        self._instance: Optional[BaseTool] = None
        self._instance_ref: Optional[weakref.ref] = None
    
    async def create_instance(self, 
                            name: str, 
                            config: Optional[Dict[str, Any]] = None,
                            dependencies: Optional[Dict[str, Any]] = None) -> BaseTool:
        """Create a tool instance.
        
        Args:
            name: Instance name
            config: Tool configuration
            dependencies: Injected dependencies
            
        Returns:
            Tool instance
        """
        # Check if singleton and instance exists
        if self.metadata.singleton:
            if self._instance_ref and self._instance_ref():
                return self._instance_ref()
            elif self._instance:
                return self._instance
        
        # Create new instance
        try:
            # Inject dependencies into constructor if supported
            instance = await self._create_with_dependencies(name, config, dependencies)
            
            # Store reference for singleton
            if self.metadata.singleton:
                if instance.__class__.__dict__.get('__weakref__'):
                    self._instance_ref = weakref.ref(instance)
                else:
                    self._instance = instance
            
            self.logger.debug(f"Created tool instance: {name}")
            return instance
            
        except Exception as e:
            self.logger.error(f"Error creating tool instance {name}: {e}")
            raise
    
    async def _create_with_dependencies(self, 
                                      name: str, 
                                      config: Optional[Dict[str, Any]],
                                      dependencies: Optional[Dict[str, Any]]) -> BaseTool:
        """Create instance with dependency injection."""
        # Get constructor signature
        sig = inspect.signature(self.tool_class.__init__)
        kwargs = {'name': name}
        
        # Add config if constructor accepts it
        if 'config' in sig.parameters:
            kwargs['config'] = config
        
        # Inject dependencies
        if dependencies:
            for param_name, param in sig.parameters.items():
                if param_name in dependencies:
                    kwargs[param_name] = dependencies[param_name]
        
        # Create instance
        if asyncio.iscoroutinefunction(self.tool_class):
            instance = await self.tool_class(**kwargs)
        else:
            instance = self.tool_class(**kwargs)
        
        return instance

class ToolRegistry:
    """Registry for managing tools with dependency injection.
    
    Provides tool registration, dependency resolution, lazy loading,
    and lifecycle management.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._factories: Dict[str, ToolFactory] = {}
        self._metadata: Dict[str, ToolMetadata] = {}
        self._instances: Dict[str, BaseTool] = {}
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._reverse_dependencies: Dict[str, Set[str]] = {}
        self._loading_lock = asyncio.Lock()
        self._disposed = False
    
    def register_tool(self, 
                     name: str, 
                     tool_class: Type[BaseTool],
                     dependencies: Optional[List[str]] = None,
                     singleton: bool = True,
                     lazy: bool = True,
                     **metadata_kwargs) -> None:
        """Register a tool class.
        
        Args:
            name: Tool name
            tool_class: Tool class
            dependencies: List of dependency names
            singleton: Whether to create singleton instances
            lazy: Whether to use lazy loading
            **metadata_kwargs: Additional metadata
        """
        if self._disposed:
            raise RuntimeError("Registry is disposed")
        
        # Get dependencies from class if not provided
        if dependencies is None:
            dependencies = getattr(tool_class, '_dependencies', [])
        
        # Create metadata
        metadata = ToolMetadata(
            name=name,
            tool_class=tool_class,
            dependencies=dependencies,
            singleton=singleton,
            lazy=lazy,
            **metadata_kwargs
        )
        
        # Create factory
        factory = ToolFactory(tool_class, metadata)
        
        # Store
        self._factories[name] = factory
        self._metadata[name] = metadata
        
        # Update dependency graph
        self._dependency_graph[name] = set(dependencies)
        for dep in dependencies:
            if dep not in self._reverse_dependencies:
                self._reverse_dependencies[dep] = set()
            self._reverse_dependencies[dep].add(name)
        
        self.logger.debug(f"Registered tool: {name} (dependencies: {dependencies})")
    
    def register_decorator(self, 
                          name: Optional[str] = None,
                          dependencies: Optional[List[str]] = None,
                          singleton: bool = True,
                          lazy: bool = True,
                          **metadata_kwargs):
        """Decorator for registering tools.
        
        Usage:
            @registry.register_decorator('my_tool')
            class MyTool(BaseTool):
                pass
        """
        def decorator(tool_class: Type[BaseTool]):
            tool_name = name or tool_class.__name__.lower()
            self.register_tool(
                tool_name, 
                tool_class, 
                dependencies, 
                singleton, 
                lazy, 
                **metadata_kwargs
            )
            return tool_class
        return decorator
    
    async def get_tool(self, name: str, config: Optional[Dict[str, Any]] = None) -> BaseTool:
        """Get a tool instance with dependency resolution.
        
        Args:
            name: Tool name
            config: Tool configuration
            
        Returns:
            Tool instance
        """
        if self._disposed:
            raise RuntimeError("Registry is disposed")
        
        async with self._loading_lock:
            return await self._get_tool_internal(name, config)
    
    async def _get_tool_internal(self, name: str, config: Optional[Dict[str, Any]] = None) -> BaseTool:
        """Internal tool retrieval with dependency resolution."""
        # Check if already instantiated
        if name in self._instances:
            instance = self._instances[name]
            if instance.is_initialized:
                return instance
        
        # Check if tool is registered
        if name not in self._factories:
            raise ValueError(f"Tool '{name}' is not registered")
        
        metadata = self._metadata[name]
        factory = self._factories[name]
        
        # Update lifecycle
        metadata.lifecycle = ToolLifecycle.INITIALIZING
        
        try:
            # Resolve dependencies
            dependencies = await self._resolve_dependencies(name, config)
            
            # Create instance
            instance = await factory.create_instance(name, config, dependencies)
            
            # Initialize if not lazy or if dependencies require it
            if not metadata.lazy or dependencies:
                await instance.initialize()
            
            # Store instance
            if metadata.singleton:
                self._instances[name] = instance
            
            # Update lifecycle
            metadata.lifecycle = ToolLifecycle.READY
            
            self.logger.debug(f"Tool '{name}' loaded successfully")
            return instance
            
        except Exception as e:
            metadata.lifecycle = ToolLifecycle.ERROR
            self.logger.error(f"Error loading tool '{name}': {e}")
            raise
    
    async def _resolve_dependencies(self, 
                                  tool_name: str, 
                                  config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resolve tool dependencies."""
        dependencies = {}
        dep_names = self._dependency_graph.get(tool_name, set())
        
        for dep_name in dep_names:
            # Recursive dependency resolution
            dep_instance = await self._get_tool_internal(dep_name, config)
            dependencies[dep_name] = dep_instance
        
        return dependencies
    
    def is_registered(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._factories
    
    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get tool metadata."""
        return self._metadata.get(name)
    
    def list_tools(self, tag: Optional[str] = None) -> List[str]:
        """List registered tools.
        
        Args:
            tag: Filter by tag
            
        Returns:
            List of tool names
        """
        if tag is None:
            return list(self._factories.keys())
        
        return [
            name for name, metadata in self._metadata.items()
            if tag in metadata.tags
        ]
    
    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """Get the dependency graph."""
        return self._dependency_graph.copy()
    
    def validate_dependencies(self) -> List[str]:
        """Validate all dependencies are resolvable.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        for tool_name, deps in self._dependency_graph.items():
            for dep in deps:
                if dep not in self._factories:
                    errors.append(f"Tool '{tool_name}' depends on unregistered tool '{dep}'")
        
        # Check for circular dependencies
        try:
            self._topological_sort()
        except ValueError as e:
            errors.append(str(e))
        
        return errors
    
    def _topological_sort(self) -> List[str]:
        """Topological sort to detect circular dependencies."""
        # Kahn's algorithm
        in_degree = {name: 0 for name in self._factories}
        
        for deps in self._dependency_graph.values():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for dependent in self._reverse_dependencies.get(current, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self._factories):
            raise ValueError("Circular dependency detected")
        
        return result
    
    async def dispose_all(self) -> None:
        """Dispose all tool instances."""
        if self._disposed:
            return
        
        self.logger.info("Disposing all tools...")
        
        # Dispose in reverse dependency order
        try:
            sorted_tools = self._topological_sort()
            sorted_tools.reverse()  # Reverse order for disposal
        except ValueError:
            # If circular dependencies, just dispose in any order
            sorted_tools = list(self._instances.keys())
        
        for tool_name in sorted_tools:
            if tool_name in self._instances:
                try:
                    await self._instances[tool_name].dispose()
                    self._metadata[tool_name].lifecycle = ToolLifecycle.DISPOSED
                except Exception as e:
                    self.logger.error(f"Error disposing tool '{tool_name}': {e}")
        
        self._instances.clear()
        self._disposed = True
        self.logger.info("All tools disposed")
    
    def discover_tools(self, package_path: Union[str, Path]) -> int:
        """Discover and register tools from a package.
        
        Args:
            package_path: Path to package containing tools
            
        Returns:
            Number of tools discovered
        """
        package_path = Path(package_path)
        discovered = 0
        
        for py_file in package_path.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                # Import module
                spec = importlib.util.spec_from_file_location(
                    py_file.stem, py_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find tool classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (inspect.isclass(attr) and 
                            issubclass(attr, BaseTool) and 
                            attr != BaseTool):
                            
                            tool_name = attr_name.lower()
                            if not self.is_registered(tool_name):
                                self.register_tool(tool_name, attr)
                                discovered += 1
                                
            except Exception as e:
                self.logger.warning(f"Error discovering tools in {py_file}: {e}")
        
        self.logger.info(f"Discovered {discovered} tools from {package_path}")
        return discovered
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        lifecycle_counts = {}
        for metadata in self._metadata.values():
            lifecycle = metadata.lifecycle.value
            lifecycle_counts[lifecycle] = lifecycle_counts.get(lifecycle, 0) + 1
        
        return {
            "total_registered": len(self._factories),
            "total_instances": len(self._instances),
            "lifecycle_counts": lifecycle_counts,
            "dependency_count": sum(len(deps) for deps in self._dependency_graph.values()),
            "disposed": self._disposed
        }