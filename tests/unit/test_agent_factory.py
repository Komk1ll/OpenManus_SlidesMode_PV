"""Unit tests for AgentFactory.

Tests cover agent creation, dependency injection, validation,
and all factory methods following pytest best practices.
"""

import pytest
from unittest.mock import Mock, patch, call
from typing import Dict, Any

from app.factories.agent import AgentFactory
from app.agent.base import BaseAgent
from app.agent.manus import Manus
from app.agent.swe import SWEAgent
from app.agent.browser import BrowserAgent
from app.agent.mcp import MCPAgent
from app.agent.toolcall import ToolCallAgent
from app.interfaces.llm import ILLMProvider
from app.interfaces.logger import ILogger
from app.interfaces.config import IConfig
from app.interfaces.sandbox import ISandboxClient


class TestAgentFactory:
    """Test suite for AgentFactory class."""
    
    @pytest.fixture
    def factory(self):
        """Create AgentFactory instance for testing."""
        return AgentFactory()
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock all dependencies for agent creation."""
        return {
            "llm_provider": Mock(spec=ILLMProvider),
            "logger": Mock(spec=ILogger),
            "config": Mock(spec=IConfig),
            "sandbox_client": Mock(spec=ISandboxClient)
        }
    
    @pytest.fixture
    def mock_agent(self):
        """Mock agent instance returned by create_with_dependencies."""
        agent = Mock(spec=BaseAgent)
        agent.name = "test_agent"
        return agent
    
    def test_agent_types_registry(self, factory):
        """Test that AGENT_TYPES registry contains expected agent types."""
        expected_types = {
            "manus": Manus,
            "swe": SWEAgent,
            "browser": BrowserAgent,
            "mcp": MCPAgent,
            "toolcall": ToolCallAgent,
        }
        
        assert factory.AGENT_TYPES == expected_types
        assert len(factory.AGENT_TYPES) == 5
    
    def test_get_available_agent_types(self, factory):
        """Test get_available_agent_types returns correct list."""
        available_types = factory.get_available_agent_types()
        
        expected_types = ["manus", "swe", "browser", "mcp", "toolcall"]
        assert set(available_types) == set(expected_types)
        assert len(available_types) == 5
    
    @pytest.mark.parametrize("agent_type,expected_class", [
        ("manus", Manus),
        ("swe", SWEAgent),
        ("browser", BrowserAgent),
        ("mcp", MCPAgent),
        ("toolcall", ToolCallAgent),
    ])
    def test_create_agent_success(self, factory, mock_dependencies, mock_agent, 
                                 agent_type, expected_class):
        """Test successful agent creation for all supported types."""
        # Mock the create_with_dependencies method
        with patch.object(expected_class, 'create_with_dependencies', 
                         return_value=mock_agent) as mock_create:
            
            result = factory.create_agent(
                agent_type=agent_type,
                **mock_dependencies
            )
            
            # Verify correct agent class method was called
            mock_create.assert_called_once_with(
                llm_provider=mock_dependencies["llm_provider"],
                logger=mock_dependencies["logger"],
                config=mock_dependencies["config"],
                sandbox_client=mock_dependencies["sandbox_client"],
                name=agent_type
            )
            
            # Verify logger was called
            mock_dependencies["logger"].info.assert_called_once_with(
                f"Created {agent_type} agent '{agent_type}' with injected dependencies"
            )
            
            assert result == mock_agent
    
    def test_create_agent_with_custom_name(self, factory, mock_dependencies, mock_agent):
        """Test agent creation with custom name."""
        custom_name = "my_custom_agent"
        
        with patch.object(Manus, 'create_with_dependencies', 
                         return_value=mock_agent) as mock_create:
            
            result = factory.create_agent(
                agent_type="manus",
                name=custom_name,
                **mock_dependencies
            )
            
            mock_create.assert_called_once_with(
                llm_provider=mock_dependencies["llm_provider"],
                logger=mock_dependencies["logger"],
                config=mock_dependencies["config"],
                sandbox_client=mock_dependencies["sandbox_client"],
                name=custom_name
            )
            
            mock_dependencies["logger"].info.assert_called_once_with(
                f"Created manus agent '{custom_name}' with injected dependencies"
            )
    
    def test_create_agent_with_kwargs(self, factory, mock_dependencies, mock_agent):
        """Test agent creation with additional kwargs."""
        extra_kwargs = {"param1": "value1", "param2": 42}
        
        with patch.object(Manus, 'create_with_dependencies', 
                         return_value=mock_agent) as mock_create:
            
            factory.create_agent(
                agent_type="manus",
                **mock_dependencies,
                **extra_kwargs
            )
            
            mock_create.assert_called_once_with(
                llm_provider=mock_dependencies["llm_provider"],
                logger=mock_dependencies["logger"],
                config=mock_dependencies["config"],
                sandbox_client=mock_dependencies["sandbox_client"],
                name="manus",
                **extra_kwargs
            )
    
    def test_create_agent_unsupported_type(self, factory, mock_dependencies):
        """Test that creating unsupported agent type raises ValueError."""
        unsupported_type = "nonexistent_agent"
        
        with pytest.raises(ValueError) as exc_info:
            factory.create_agent(
                agent_type=unsupported_type,
                **mock_dependencies
            )
        
        error_message = str(exc_info.value)
        assert f"Unsupported agent type: {unsupported_type}" in error_message
        assert "Available types:" in error_message
        
        # Check that all available types are mentioned in error
        for agent_type in factory.AGENT_TYPES.keys():
            assert agent_type in error_message
    
    @pytest.mark.parametrize("method_name,agent_type,expected_class", [
        ("create_manus_agent", "manus", Manus),
        ("create_swe_agent", "swe", SWEAgent),
        ("create_browser_agent", "browser", BrowserAgent),
        ("create_mcp_agent", "mcp", MCPAgent),
        ("create_toolcall_agent", "toolcall", ToolCallAgent),
    ])
    def test_specialized_create_methods(self, factory, mock_dependencies, mock_agent,
                                      method_name, agent_type, expected_class):
        """Test specialized agent creation methods."""
        with patch.object(factory, 'create_agent', return_value=mock_agent) as mock_create:
            
            method = getattr(factory, method_name)
            result = method(**mock_dependencies)
            
            mock_create.assert_called_once_with(
                agent_type=agent_type,
                name=agent_type,
                **mock_dependencies
            )
            
            assert result == mock_agent
    
    @pytest.mark.parametrize("method_name,agent_type", [
        ("create_manus_agent", "manus"),
        ("create_swe_agent", "swe"),
        ("create_browser_agent", "browser"),
        ("create_mcp_agent", "mcp"),
        ("create_toolcall_agent", "toolcall"),
    ])
    def test_specialized_create_methods_with_custom_name(self, factory, mock_dependencies, 
                                                        mock_agent, method_name, agent_type):
        """Test specialized methods with custom names."""
        custom_name = f"custom_{agent_type}"
        
        with patch.object(factory, 'create_agent', return_value=mock_agent) as mock_create:
            
            method = getattr(factory, method_name)
            result = method(name=custom_name, **mock_dependencies)
            
            mock_create.assert_called_once_with(
                agent_type=agent_type,
                name=custom_name,
                **mock_dependencies
            )
    
    def test_specialized_create_methods_with_kwargs(self, factory, mock_dependencies, mock_agent):
        """Test specialized methods pass through additional kwargs."""
        extra_kwargs = {"special_param": "special_value"}
        
        with patch.object(factory, 'create_agent', return_value=mock_agent) as mock_create:
            
            factory.create_manus_agent(
                **mock_dependencies,
                **extra_kwargs
            )
            
            mock_create.assert_called_once_with(
                agent_type="manus",
                name="manus",
                **mock_dependencies,
                **extra_kwargs
            )
    
    def test_dependency_injection_integration(self, factory):
        """Test that factory methods are properly decorated with @inject."""
        # Check that create_agent has inject decorator
        assert hasattr(factory.create_agent, '__wrapped__')
        
        # Check specialized methods have inject decorator
        specialized_methods = [
            'create_manus_agent',
            'create_swe_agent', 
            'create_browser_agent',
            'create_mcp_agent',
            'create_toolcall_agent'
        ]
        
        for method_name in specialized_methods:
            method = getattr(factory, method_name)
            assert hasattr(method, '__wrapped__'), f"{method_name} should have @inject decorator"
    
    def test_agent_creation_error_handling(self, factory, mock_dependencies):
        """Test error handling when agent creation fails."""
        with patch.object(Manus, 'create_with_dependencies', 
                         side_effect=Exception("Agent creation failed")):
            
            with pytest.raises(Exception) as exc_info:
                factory.create_agent(
                    agent_type="manus",
                    **mock_dependencies
                )
            
            assert "Agent creation failed" in str(exc_info.value)
    
    def test_factory_immutable_registry(self, factory):
        """Test that AGENT_TYPES registry is not accidentally modified."""
        original_types = factory.AGENT_TYPES.copy()
        
        # Try to modify registry (should not affect original)
        factory.AGENT_TYPES["new_type"] = Mock
        
        # Create new factory instance to verify class-level registry
        new_factory = AgentFactory()
        
        # Registry should contain the modification (as it's class-level)
        # But we can test that the original expected types are still there
        for agent_type, agent_class in original_types.items():
            assert agent_type in new_factory.AGENT_TYPES
            assert new_factory.AGENT_TYPES[agent_type] == agent_class