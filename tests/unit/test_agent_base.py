"""Unit tests for base agent classes."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Optional

from app.agent.base import BaseAgent
from app.schema import AgentState, Memory, Message
from app.interfaces.llm import ILLMProvider
from app.interfaces.logger import ILogger
from app.interfaces.config import IConfig
from app.interfaces.sandbox import ISandboxClient


class MockAgent(BaseAgent):
    """Mock agent for testing BaseAgent functionality."""
    
    name: str = "mock_agent"
    description: str = "A mock agent for testing"
    step_counter: int = 0
    
    async def step(self) -> str:
        """Mock step implementation."""
        self.step_counter += 1
        return f"Step {self.step_counter} completed"


class TestBaseAgent:
    """Test cases for BaseAgent class."""

    def test_agent_initialization_basic(self, mock_llm) -> None:
        """Test basic agent initialization."""
        agent = MockAgent()
        
        assert agent.name == "mock_agent"
        assert agent.description == "A mock agent for testing"
        assert agent.state == AgentState.IDLE
        assert isinstance(agent.memory, Memory)
        assert agent.max_steps == 10
        assert agent.current_step == 0

    def test_agent_initialization_with_params(self, mock_llm) -> None:
        """Test agent initialization with custom parameters."""
        agent = MockAgent(
            name="custom_agent",
            description="Custom description",
            max_steps=20
        )
        
        assert agent.name == "custom_agent"
        assert agent.description == "Custom description"
        assert agent.max_steps == 20

    def test_agent_with_dependency_injection(self, mock_llm) -> None:
        """Test agent creation with dependency injection."""
        mock_llm_provider = Mock(spec=ILLMProvider)
        mock_logger = Mock(spec=ILogger)
        mock_config = Mock(spec=IConfig)
        mock_sandbox = Mock(spec=ISandboxClient)
        
        agent = MockAgent(
            llm_provider=mock_llm_provider,
            logger=mock_logger,
            config=mock_config,
            sandbox_client=mock_sandbox
        )
        
        assert agent.injected_llm_provider is mock_llm_provider
        assert agent.injected_logger is mock_logger
        assert agent.injected_config is mock_config
        assert agent.injected_sandbox_client is mock_sandbox

    def test_create_with_dependencies_factory(self) -> None:
        """Test factory method for creating agent with dependencies."""
        mock_llm = Mock(spec=ILLMProvider)
        mock_logger = Mock(spec=ILogger)
        mock_config = Mock(spec=IConfig)
        mock_sandbox = Mock(spec=ISandboxClient)
        
        agent = MockAgent.create_with_dependencies(
            llm_provider=mock_llm,
            logger=mock_logger,
            config=mock_config,
            sandbox_client=mock_sandbox,
            name="factory_agent"
        )
        
        assert agent.name == "factory_agent"
        assert agent.injected_llm_provider is mock_llm

    @pytest.mark.asyncio
    async def test_state_context_manager(self) -> None:
        """Test state context manager functionality."""
        agent = MockAgent()
        
        assert agent.state == AgentState.IDLE
        
        async with agent.state_context(AgentState.RUNNING):
            assert agent.state == AgentState.RUNNING
        
        assert agent.state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_state_context_manager_with_exception(self) -> None:
        """Test state context manager handles exceptions."""
        agent = MockAgent()
        
        with pytest.raises(ValueError):
            async with agent.state_context(AgentState.RUNNING):
                assert agent.state == AgentState.RUNNING
                raise ValueError("Test exception")
        
        assert agent.state == AgentState.ERROR

    def test_state_context_manager_invalid_state(self) -> None:
        """Test state context manager with invalid state."""
        agent = MockAgent()
        
        with pytest.raises(ValueError, match="Invalid state"):
            agent.state_context("invalid_state")  # type: ignore

    def test_update_memory_user_message(self) -> None:
        """Test updating memory with user message."""
        agent = MockAgent()
        initial_count = len(agent.memory.messages)
        
        agent.update_memory("user", "Hello, agent!")
        
        assert len(agent.memory.messages) == initial_count + 1
        latest_message = agent.memory.messages[-1]
        assert latest_message.role == "user"
        assert latest_message.content == "Hello, agent!"

    def test_update_memory_system_message(self) -> None:
        """Test updating memory with system message."""
        agent = MockAgent()
        agent.update_memory("system", "System initialization")
        
        latest_message = agent.memory.messages[-1]
        assert latest_message.role == "system"
        assert latest_message.content == "System initialization"

    def test_update_memory_assistant_message(self) -> None:
        """Test updating memory with assistant message."""
        agent = MockAgent()
        agent.update_memory("assistant", "I understand")
        
        latest_message = agent.memory.messages[-1]
        assert latest_message.role == "assistant"
        assert latest_message.content == "I understand"

    def test_update_memory_tool_message(self) -> None:
        """Test updating memory with tool message."""
        agent = MockAgent()
        agent.update_memory("tool", "Tool output", tool_call_id="call_123")
        
        latest_message = agent.memory.messages[-1]
        assert latest_message.role == "tool"
        assert latest_message.content == "Tool output"

    def test_update_memory_with_image(self) -> None:
        """Test updating memory with base64 image."""
        agent = MockAgent()
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        agent.update_memory("user", "Here's an image", base64_image=image_data)
        
        latest_message = agent.memory.messages[-1]
        assert latest_message.role == "user"
        assert latest_message.content == "Here's an image"

    def test_update_memory_invalid_role(self) -> None:
        """Test updating memory with invalid role raises error."""
        agent = MockAgent()
        
        with pytest.raises(ValueError, match="Unsupported message role"):
            agent.update_memory("invalid_role", "content")  # type: ignore

    @pytest.mark.asyncio
    async def test_run_basic_execution(self) -> None:
        """Test basic run execution."""
        agent = MockAgent()
        agent.max_steps = 3
        
        with patch.object(agent, 'injected_sandbox_client') as mock_sandbox:
            mock_sandbox.cleanup = AsyncMock()
            
            result = await agent.run("Test request")
            
            assert "Step 1: Step 1 completed" in result
            assert "Step 2: Step 2 completed" in result
            assert "Step 3: Step 3 completed" in result
            assert agent.current_step == 0  # Reset after completion
            mock_sandbox.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_with_max_steps_reached(self) -> None:
        """Test run execution when max steps is reached."""
        agent = MockAgent()
        agent.max_steps = 2
        
        with patch.object(agent, 'injected_sandbox_client') as mock_sandbox:
            mock_sandbox.cleanup = AsyncMock()
            
            result = await agent.run()
            
            assert "Terminated: Reached max steps (2)" in result
            assert agent.state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_run_not_idle_state_error(self) -> None:
        """Test run raises error when not in IDLE state."""
        agent = MockAgent()
        agent.state = AgentState.RUNNING
        
        with pytest.raises(RuntimeError, match="Cannot run agent from state"):
            await agent.run()

    def test_is_stuck_detection_no_messages(self) -> None:
        """Test stuck detection with no messages."""
        agent = MockAgent()
        assert not agent.is_stuck()

    def test_is_stuck_detection_insufficient_messages(self) -> None:
        """Test stuck detection with insufficient messages."""
        agent = MockAgent()
        agent.update_memory("assistant", "First response")
        assert not agent.is_stuck()

    def test_is_stuck_detection_no_duplicates(self) -> None:
        """Test stuck detection with no duplicate responses."""
        agent = MockAgent()
        agent.update_memory("assistant", "First response")
        agent.update_memory("user", "User input")
        agent.update_memory("assistant", "Second response")
        
        assert not agent.is_stuck()

    def test_is_stuck_detection_with_duplicates(self) -> None:
        """Test stuck detection with duplicate responses."""
        agent = MockAgent()
        duplicate_content = "Same response"
        
        # Add enough duplicate assistant messages to trigger stuck detection
        agent.update_memory("assistant", duplicate_content)
        agent.update_memory("user", "User input 1")
        agent.update_memory("assistant", duplicate_content)
        agent.update_memory("user", "User input 2")
        agent.update_memory("assistant", duplicate_content)  # This should trigger stuck
        
        assert agent.is_stuck()

    def test_handle_stuck_state(self) -> None:
        """Test stuck state handling."""
        agent = MockAgent()
        original_prompt = agent.next_step_prompt
        
        agent.handle_stuck_state()
        
        assert agent.next_step_prompt != original_prompt
        assert "duplicate responses" in agent.next_step_prompt.lower()

    def test_messages_property_getter(self) -> None:
        """Test messages property getter."""
        agent = MockAgent()
        agent.update_memory("user", "Test message")
        
        messages = agent.messages
        assert len(messages) == 1
        assert messages[0].content == "Test message"

    def test_messages_property_setter(self) -> None:
        """Test messages property setter."""
        agent = MockAgent()
        new_messages = [Message(role="user", content="New message")]
        
        agent.messages = new_messages
        
        assert len(agent.messages) == 1
        assert agent.messages[0].content == "New message"

    def test_injected_logger_fallback(self) -> None:
        """Test injected logger falls back to global logger."""
        agent = MockAgent()
        
        # Without DI, should fall back to global logger
        assert agent.injected_logger is not None

    def test_injected_sandbox_client_fallback(self) -> None:
        """Test injected sandbox client falls back to global client."""
        agent = MockAgent()
        
        # Without DI, should fall back to global sandbox client
        assert agent.injected_sandbox_client is not None


class ErrorAgent(BaseAgent):
    """Mock agent that raises errors for testing."""
    
    name: str = "error_agent"
    
    async def step(self) -> str:
        """Step that raises an error."""
        raise ValueError("Step error")


class TestBaseAgentErrorHandling:
    """Test error handling in BaseAgent."""

    @pytest.mark.asyncio
    async def test_run_with_step_error(self) -> None:
        """Test run handling step errors."""
        agent = ErrorAgent()
        
        with patch.object(agent, 'injected_sandbox_client') as mock_sandbox:
            mock_sandbox.cleanup = AsyncMock()
            
            # The error should be caught and handled gracefully
            with pytest.raises(ValueError):
                await agent.run()


class TestBaseAgentDependencyInjection:
    """Test dependency injection features."""

    def test_di_properties_when_none(self) -> None:
        """Test DI properties return None when not injected."""
        agent = MockAgent()
        
        assert agent.injected_llm_provider is None
        assert agent.injected_config is None
        # Logger and sandbox should have fallbacks
        assert agent.injected_logger is not None
        assert agent.injected_sandbox_client is not None

    def test_di_properties_when_injected(self) -> None:
        """Test DI properties return injected instances."""
        mock_llm = Mock(spec=ILLMProvider)
        mock_logger = Mock(spec=ILogger)
        mock_config = Mock(spec=IConfig)
        mock_sandbox = Mock(spec=ISandboxClient)
        
        agent = MockAgent(
            llm_provider=mock_llm,
            logger=mock_logger,
            config=mock_config,
            sandbox_client=mock_sandbox
        )
        
        assert agent.injected_llm_provider is mock_llm
        assert agent.injected_logger is mock_logger
        assert agent.injected_config is mock_config
        assert agent.injected_sandbox_client is mock_sandbox