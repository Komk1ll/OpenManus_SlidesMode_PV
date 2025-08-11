"""Configuration management for the presentation system.

Provides centralized configuration management with support for
environment variables, file-based configs, and runtime updates.
"""

from typing import Any, Dict, Optional, Union, List, Type, TypeVar
from pathlib import Path
import os
import json
import yaml
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime

T = TypeVar('T')

@dataclass
class ConfigSource:
    """Configuration source metadata."""
    name: str
    type: str  # 'file', 'env', 'dict', 'remote'
    path: Optional[str] = None
    priority: int = 0  # Higher priority overrides lower
    last_modified: Optional[datetime] = None
    
class ConfigProvider(ABC):
    """Abstract base class for configuration providers."""
    
    @abstractmethod
    async def load(self) -> Dict[str, Any]:
        """Load configuration data."""
        pass
    
    @abstractmethod
    async def save(self, config: Dict[str, Any]) -> None:
        """Save configuration data."""
        pass
    
    @abstractmethod
    def watch(self, callback) -> None:
        """Watch for configuration changes."""
        pass

class FileConfigProvider(ConfigProvider):
    """File-based configuration provider."""
    
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._watchers = []
    
    async def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.file_path.exists():
            return {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                if self.file_path.suffix.lower() == '.json':
                    return json.load(f)
                elif self.file_path.suffix.lower() in ['.yml', '.yaml']:
                    return yaml.safe_load(f) or {}
                else:
                    # Try to parse as JSON first, then YAML
                    content = f.read()
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return yaml.safe_load(content) or {}
        except Exception as e:
            self.logger.error(f"Error loading config from {self.file_path}: {e}")
            return {}
    
    async def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                if self.file_path.suffix.lower() == '.json':
                    json.dump(config, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.debug(f"Config saved to {self.file_path}")
        except Exception as e:
            self.logger.error(f"Error saving config to {self.file_path}: {e}")
            raise
    
    def watch(self, callback) -> None:
        """Watch for file changes."""
        self._watchers.append(callback)
        # Note: File watching implementation would require additional dependencies
        # like watchdog. For now, we just store the callback.

class EnvironmentConfigProvider(ConfigProvider):
    """Environment variable configuration provider."""
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def load(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        for key, value in os.environ.items():
            if self.prefix and not key.startswith(self.prefix):
                continue
            
            # Remove prefix and convert to nested dict
            config_key = key[len(self.prefix):] if self.prefix else key
            config_key = config_key.lower()
            
            # Convert string values to appropriate types
            config[config_key] = self._convert_value(value)
        
        return config
    
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        
        # Return as string
        return value
    
    async def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to environment (not persistent)."""
        for key, value in config.items():
            env_key = f"{self.prefix}{key.upper()}" if self.prefix else key.upper()
            os.environ[env_key] = str(value)
    
    def watch(self, callback) -> None:
        """Environment variables don't support watching."""
        pass

class DictConfigProvider(ConfigProvider):
    """In-memory dictionary configuration provider."""
    
    def __init__(self, initial_config: Optional[Dict[str, Any]] = None):
        self._config = initial_config or {}
        self._watchers = []
    
    async def load(self) -> Dict[str, Any]:
        """Load configuration from memory."""
        return self._config.copy()
    
    async def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to memory."""
        self._config = config.copy()
        
        # Notify watchers
        for callback in self._watchers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(config)
                else:
                    callback(config)
            except Exception as e:
                logging.error(f"Error in config watcher: {e}")
    
    def watch(self, callback) -> None:
        """Watch for configuration changes."""
        self._watchers.append(callback)

class ConfigManager:
    """Centralized configuration manager.
    
    Supports multiple configuration sources with priority-based merging,
    environment variable interpolation, and runtime configuration updates.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._providers: List[tuple[ConfigProvider, ConfigSource]] = []
        self._config: Dict[str, Any] = {}
        self._watchers = []
        self._loaded = False
    
    def add_provider(self, provider: ConfigProvider, source: ConfigSource) -> None:
        """Add a configuration provider.
        
        Args:
            provider: Configuration provider instance
            source: Source metadata
        """
        self._providers.append((provider, source))
        self._providers.sort(key=lambda x: x[1].priority, reverse=True)
        self.logger.debug(f"Added config provider: {source.name} (priority: {source.priority})")
    
    def add_file_source(self, file_path: Union[str, Path], priority: int = 0) -> None:
        """Add a file-based configuration source."""
        provider = FileConfigProvider(file_path)
        source = ConfigSource(
            name=f"file:{file_path}",
            type="file",
            path=str(file_path),
            priority=priority
        )
        self.add_provider(provider, source)
    
    def add_env_source(self, prefix: str = "", priority: int = 100) -> None:
        """Add environment variable configuration source."""
        provider = EnvironmentConfigProvider(prefix)
        source = ConfigSource(
            name=f"env:{prefix}",
            type="env",
            priority=priority
        )
        self.add_provider(provider, source)
    
    def add_dict_source(self, config: Dict[str, Any], name: str = "dict", priority: int = 50) -> None:
        """Add dictionary configuration source."""
        provider = DictConfigProvider(config)
        source = ConfigSource(
            name=name,
            type="dict",
            priority=priority
        )
        self.add_provider(provider, source)
    
    async def load(self) -> None:
        """Load configuration from all sources."""
        merged_config = {}
        
        # Load from all providers in priority order (highest first)
        for provider, source in self._providers:
            try:
                config = await provider.load()
                if config:
                    # Merge with lower priority configs
                    merged_config = self._deep_merge(config, merged_config)
                    self.logger.debug(f"Loaded config from {source.name}")
            except Exception as e:
                self.logger.error(f"Error loading config from {source.name}: {e}")
        
        # Interpolate environment variables
        self._config = self._interpolate_env_vars(merged_config)
        self._loaded = True
        
        self.logger.info(f"Configuration loaded from {len(self._providers)} sources")
    
    def _deep_merge(self, source: Dict[str, Any], destination: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with source taking precedence."""
        result = destination.copy()
        
        for key, value in source.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(value, result[key])
            else:
                result[key] = value
        
        return result
    
    def _interpolate_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Interpolate environment variables in config values."""
        def interpolate_value(value):
            if isinstance(value, str):
                # Replace ${VAR} or $VAR with environment variable
                import re
                pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
                
                def replace_var(match):
                    var_name = match.group(1) or match.group(2)
                    return os.environ.get(var_name, match.group(0))
                
                return re.sub(pattern, replace_var, value)
            elif isinstance(value, dict):
                return {k: interpolate_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [interpolate_value(item) for item in value]
            else:
                return value
        
        return interpolate_value(config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Supports dot notation for nested keys (e.g., 'database.host').
        """
        if not self._loaded:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_typed(self, key: str, type_class: Type[T], default: Optional[T] = None) -> Optional[T]:
        """Get configuration value with type conversion."""
        value = self.get(key, default)
        
        if value is None:
            return default
        
        if isinstance(value, type_class):
            return value
        
        try:
            # Try to convert
            if type_class == bool and isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            else:
                return type_class(value)
        except (ValueError, TypeError):
            self.logger.warning(f"Cannot convert {key}={value} to {type_class.__name__}")
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        if not self._loaded:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Notify watchers
        self._notify_watchers()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        if not self._loaded:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        
        self._config = self._deep_merge(updates, self._config)
        self._notify_watchers()
    
    def watch(self, callback) -> None:
        """Watch for configuration changes."""
        self._watchers.append(callback)
    
    def _notify_watchers(self) -> None:
        """Notify all watchers of configuration changes."""
        for callback in self._watchers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(self._config.copy()))
                else:
                    callback(self._config.copy())
            except Exception as e:
                self.logger.error(f"Error in config watcher: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        if not self._loaded:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        
        return self._config.copy()
    
    def get_sources(self) -> List[ConfigSource]:
        """Get information about all configuration sources."""
        return [source for _, source in self._providers]
    
    async def reload(self) -> None:
        """Reload configuration from all sources."""
        await self.load()
        self._notify_watchers()
        self.logger.info("Configuration reloaded")