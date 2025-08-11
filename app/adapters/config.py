"""Configuration Adapter implementing IConfig interface."""

from pathlib import Path
from typing import Any, Dict, List, Union

from app.config import Config as LegacyConfig
from app.interfaces.config import IConfig


class AppConfig(IConfig):
    """Configuration adapter wrapping the legacy Config singleton.
    
    Provides a clean interface to the existing configuration system
    while maintaining backward compatibility.
    """

    def __init__(self, config: LegacyConfig = None):
        """Initialize the config adapter.
        
        Args:
            config: Optional legacy config instance. If None, uses the singleton.
        """
        self._config = config or LegacyConfig()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._get_nested_value(key, default)

    def get_str(self, key: str, default: str = "") -> str:
        """Get a string configuration value.
        
        Args:
            key: Configuration key
            default: Default string value
            
        Returns:
            String configuration value
        """
        return str(self._get_nested_value(key, default))

    def get_string(self, key: str, default: str = "") -> str:
        """Get a string configuration value."""
        return str(self._get_nested_value(key, default))

    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer configuration value."""
        value = self._get_nested_value(key, default)
        return int(value) if value is not None else default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a float configuration value."""
        value = self._get_nested_value(key, default)
        return float(value) if value is not None else default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value."""
        value = self._get_nested_value(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value) if value is not None else default

    def get_list(self, key: str, default: List[Any] = None) -> List[Any]:
        """Get a list configuration value."""
        if default is None:
            default = []
        value = self._get_nested_value(key, default)
        return list(value) if value is not None else default

    def get_dict(self, key: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a dictionary configuration value."""
        if default is None:
            default = {}
        value = self._get_nested_value(key, default)
        return dict(value) if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Note: This implementation doesn't persist changes to file.
        For runtime configuration changes only.
        """
        # For now, we'll store runtime overrides in a separate dict
        if not hasattr(self, '_runtime_overrides'):
            self._runtime_overrides = {}
        
        # Support nested keys like 'llm.default.model'
        keys = key.split('.')
        current = self._runtime_overrides
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    def has(self, key: str) -> bool:
        """Check if a configuration key exists."""
        try:
            self._get_nested_value(key)
            return True
        except (AttributeError, KeyError, TypeError):
            return False

    @property
    def workspace_root(self) -> str:
        """Get the workspace root directory."""
        return str(self._config.workspace_root)

    @property
    def log_level(self) -> str:
        """Get the log level."""
        # Default to INFO if not configured
        return self.get_string('logging.level', 'INFO')

    def _get_nested_value(self, key: str, default: Any = None) -> Any:
        """Get a nested configuration value using dot notation.
        
        Args:
            key: Dot-separated key path (e.g., 'llm.default.model')
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        # Check runtime overrides first
        if hasattr(self, '_runtime_overrides'):
            try:
                value = self._get_from_dict(self._runtime_overrides, key)
                if value is not None:
                    return value
            except (KeyError, TypeError):
                pass
        
        # Check legacy config
        keys = key.split('.')
        
        # Handle special cases for legacy config structure
        if keys[0] == 'llm':
            llm_config = self._config.llm
            if len(keys) == 1:
                return llm_config
            elif len(keys) >= 2:
                llm_name = keys[1]
                if llm_name in llm_config:
                    if len(keys) == 2:
                        return llm_config[llm_name]
                    else:
                        # Get specific LLM setting
                        llm_settings = llm_config[llm_name]
                        attr_name = keys[2]
                        return getattr(llm_settings, attr_name, default)
        
        elif keys[0] == 'sandbox':
            sandbox_config = self._config.sandbox
            if len(keys) == 1:
                return sandbox_config
            elif len(keys) == 2 and sandbox_config:
                return getattr(sandbox_config, keys[1], default)
        
        elif keys[0] == 'browser':
            browser_config = self._config.browser_config
            if len(keys) == 1:
                return browser_config
            elif len(keys) == 2 and browser_config:
                return getattr(browser_config, keys[1], default)
        
        elif keys[0] == 'search':
            search_config = self._config.search_config
            if len(keys) == 1:
                return search_config
            elif len(keys) == 2 and search_config:
                return getattr(search_config, keys[1], default)
        
        elif keys[0] == 'mcp':
            mcp_config = self._config.mcp_config
            if len(keys) == 1:
                return mcp_config
            elif len(keys) == 2 and mcp_config:
                return getattr(mcp_config, keys[1], default)
        
        # Fallback: try to get from root config object
        try:
            current = self._config
            for k in keys:
                if hasattr(current, k):
                    current = getattr(current, k)
                else:
                    return default
            return current
        except (AttributeError, TypeError):
            return default
    
    def _get_from_dict(self, data: Dict[str, Any], key: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = key.split('.')
        current = data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                raise KeyError(f"Key '{key}' not found")
        return current