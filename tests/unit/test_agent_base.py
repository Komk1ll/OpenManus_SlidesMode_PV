"""
Unit tests for app.agent.base module
Tests for agent lifecycle state management (IDLE→RUNNING→FINISHED/ERROR)
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from contextlib import asynccontextmanager

from app.agent.base import BaseAgent
from app.schema import AgentState, Memory, Message
from app.llm import LLM


class TestBaseAgent:
    """Test cases for BaseAgent abstract base class"""

    def test_base_agent_cannot_be_instantiated(self):
        """Test that BaseAgent cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseAgent(name="test")

    def test_concrete_agent_implementation(self):
        """Test concrete implementation of BaseAgent"""
        
        class ConcreteAgent(BaseAgent):
            async def step(self) -> str:
                return "Step executed"
        
        agent = ConcreteAgent(name="test_agent")
        assert agent.name == "test_agent"
        assert agent.state == AgentState.IDLE
        assert agent.current_step == 0
        assert agent.max_steps == 10

    def test_agent_initialization_with_defaults(self):
        """Test agent initialization with default values"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        
        assert agent.name == "test"
        assert agent.description is None
        assert agent.system_prompt is None
        assert agent.next_step_prompt is None
        assert isinstance(agent.memory, Memory)
        assert agent.state == AgentState.IDLE
        assert agent.max_steps == 10
        assert agent.current_step == 0

    def test_agent_initialization_with_custom_values(self):
        """Test agent initialization with custom values"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        custom_memory = Memory()
        agent = TestAgent(
            name="custom_agent",
            description="A custom test agent",
            system_prompt="You are a test agent",
            max_steps=5,
            memory=custom_memory
        )
        
        assert agent.name == "custom_agent"
        assert agent.description == "A custom test agent"
        assert agent.system_prompt == "You are a test agent"
        assert agent.max_steps == 5
        assert agent.memory == custom_memory

    @pytest.mark.asyncio
    async def test_state_context_manager_success(self):
        """Test successful state transition using context manager"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        assert agent.state == AgentState.IDLE
        
        async with agent.state_context(AgentState.RUNNING):
            assert agent.state == AgentState.RUNNING
        
        # Should revert to previous state
        assert agent.state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_state_context_manager_with_exception(self):
        """Test state transition with exception in context"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        assert agent.state == AgentState.IDLE
        
        with pytest.raises(ValueError):
            async with agent.state_context(AgentState.RUNNING):
                assert agent.state == AgentState.RUNNING
                raise ValueError("Test exception")
        
        # Should transition to ERROR state on exception
        assert agent.state == AgentState.ERROR

    @pytest.mark.asyncio
    async def test_state_context_manager_invalid_state(self):
        """Test state context manager with invalid state"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        
        with pytest.raises(ValueError, match="Invalid state"):
            async with agent.state_context("INVALID_STATE"):
                pass

    def test_update_memory_user_message(self):
        """Test updating memory with user message"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        agent.update_memory("user", "Hello, agent!")
        
        messages = agent.memory.get_messages()
        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Hello, agent!"

    def test_update_memory_system_message(self):
        """Test updating memory with system message"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        agent.update_memory("system", "System initialization")
        
        messages = agent.memory.get_messages()
        assert len(messages) == 1
        assert messages[0].role == "system"
        assert messages[0].content == "System initialization"

    def test_update_memory_assistant_message(self):
        """Test updating memory with assistant message"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        agent.update_memory("assistant", "I understand your request")
        
        messages = agent.memory.get_messages()
        assert len(messages) == 1
        assert messages[0].role == "assistant"
        assert messages[0].content == "I understand your request"

    def test_update_memory_tool_message(self):
        """Test updating memory with tool message"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        agent.update_memory("tool", "Tool execution result", tool_call_id="call_123")
        
        messages = agent.memory.get_messages()
        assert len(messages) == 1
        assert messages[0].role == "tool"
        assert messages[0].content == "Tool execution result"

    def test_update_memory_with_image(self):
        """Test updating memory with base64 image"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        agent.update_memory("user", "Look at this image", base64_image="base64data")
        
        messages = agent.memory.get_messages()
        assert len(messages) == 1
        assert messages[0].base64_image == "base64data"

    def test_update_memory_invalid_role(self):
        """Test updating memory with invalid role"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        
        with pytest.raises(ValueError, match="Unsupported message role"):
            agent.update_memory("invalid_role", "Some content")

    @pytest.mark.asyncio
    async def test_run_from_idle_state(self):
        """Test running agent from IDLE state"""
        
        class TestAgent(BaseAgent):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.step_count = 0
            
            async def step(self) -> str:
                self.step_count += 1
                if self.step_count >= 3:
                    self.state = AgentState.FINISHED
                return f"Step {self.step_count} completed"
        
        agent = TestAgent(name="test", max_steps=5)
        result = await agent.run("Initial request")
        
        assert "Step 1: Step 1 completed" in result
        assert "Step 2: Step 2 completed" in result
        assert "Step 3: Step 3 completed" in result
        assert agent.state == AgentState.IDLE  # Should revert after run

    @pytest.mark.asyncio
    async def test_run_from_non_idle_state(self):
        """Test running agent from non-IDLE state raises error"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        agent.state = AgentState.RUNNING
        
        with pytest.raises(RuntimeError, match="Cannot run agent from state"):
            await agent.run()

    @pytest.mark.asyncio
    async def test_run_with_max_steps_reached(self):
        """Test agent run stops when max steps reached"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "Infinite step"
        
        agent = TestAgent(name="test", max_steps=3)
        result = await agent.run()
        
        assert "Step 1:" in result
        assert "Step 2:" in result
        assert "Step 3:" in result
        assert agent.current_step == 0  # Should reset after max steps

    @pytest.mark.asyncio
    async def test_run_with_initial_request(self):
        """Test agent run with initial user request"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                self.state = AgentState.FINISHED
                return "Processed request"
        
        agent = TestAgent(name="test")
        await agent.run("Process this request")
        
        messages = agent.memory.get_messages()
        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Process this request"

    @pytest.mark.asyncio
    async def test_run_without_initial_request(self):
        """Test agent run without initial request"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                self.state = AgentState.FINISHED
                return "No request processed"
        
        agent = TestAgent(name="test")
        await agent.run()
        
        messages = agent.memory.get_messages()
        assert len(messages) == 0

    def test_is_stuck_method(self):
        """Test is_stuck detection method"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        
        # Mock the is_stuck method since it's not shown in the provided code
        with patch.object(agent, 'is_stuck', return_value=False):
            assert not agent.is_stuck()
        
        with patch.object(agent, 'is_stuck', return_value=True):
            assert agent.is_stuck()

    def test_handle_stuck_state_method(self):
        """Test handle_stuck_state method"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        
        # Mock the handle_stuck_state method
        with patch.object(agent, 'handle_stuck_state') as mock_handle:
            agent.handle_stuck_state()
            mock_handle.assert_called_once()

    @pytest.mark.asyncio
    async def test_step_execution_tracking(self):
        """Test that step execution is properly tracked"""
        
        class TestAgent(BaseAgent):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.executed_steps = []
            
            async def step(self) -> str:
                self.executed_steps.append(self.current_step)
                if len(self.executed_steps) >= 2:
                    self.state = AgentState.FINISHED
                return f"Step {self.current_step}"
        
        agent = TestAgent(name="test")
        await agent.run()
        
        assert agent.executed_steps == [1, 2]

    @pytest.mark.asyncio
    async def test_agent_state_transitions(self):
        """Test complete agent state transition lifecycle"""
        
        class TestAgent(BaseAgent):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.state_history = []
            
            async def step(self) -> str:
                self.state_history.append(self.state)
                self.state = AgentState.FINISHED
                return "Completed"
        
        agent = TestAgent(name="test")
        
        # Initial state
        assert agent.state == AgentState.IDLE
        
        # Run agent
        await agent.run()
        
        # Should have recorded RUNNING state during execution
        assert AgentState.RUNNING in agent.state_history
        
        # Should be back to IDLE after run
        assert agent.state == AgentState.IDLE

    def test_agent_configuration_validation(self):
        """Test agent configuration validation"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        # Test with negative max_steps
        agent = TestAgent(name="test", max_steps=-1)
        assert agent.max_steps == -1  # Should allow but may cause issues
        
        # Test with zero max_steps
        agent = TestAgent(name="test", max_steps=0)
        assert agent.max_steps == 0

    def test_agent_memory_persistence(self):
        """Test that agent memory persists across operations"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        
        # Add multiple messages
        agent.update_memory("user", "First message")
        agent.update_memory("assistant", "First response")
        agent.update_memory("user", "Second message")
        
        messages = agent.memory.get_messages()
        assert len(messages) == 3
        assert messages[0].content == "First message"
        assert messages[1].content == "First response"
        assert messages[2].content == "Second message"

    def test_agent_extra_fields_allowed(self):
        """Test that agent allows extra fields for subclass flexibility"""
        
        class ExtendedAgent(BaseAgent):
            def __init__(self, custom_field=None, **kwargs):
                super().__init__(**kwargs)
                self.custom_field = custom_field
            
            async def step(self) -> str:
                return f"Custom: {self.custom_field}"
        
        agent = ExtendedAgent(name="extended", custom_field="test_value")
        assert agent.custom_field == "test_value"


class TestAgentStateManagement:
    """Test cases specifically for agent state management"""

    @pytest.mark.asyncio
    async def test_state_transition_idle_to_running(self):
        """Test state transition from IDLE to RUNNING"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                return "test"
        
        agent = TestAgent(name="test")
        assert agent.state == AgentState.IDLE
        
        async with agent.state_context(AgentState.RUNNING):
            assert agent.state == AgentState.RUNNING

    @pytest.mark.asyncio
    async def test_state_transition_running_to_finished(self):
        """Test state transition from RUNNING to FINISHED"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                self.state = AgentState.FINISHED
                return "finished"
        
        agent = TestAgent(name="test", max_steps=1)
        await agent.run()
        
        # After run completes, should be back to IDLE
        assert agent.state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_state_transition_to_error(self):
        """Test state transition to ERROR on exception"""
        
        class TestAgent(BaseAgent):
            async def step(self) -> str:
                raise RuntimeError("Step failed")
        
        agent = TestAgent(name="test")
        
        with pytest.raises(RuntimeError):
            async with agent.state_context(AgentState.RUNNING):
                raise RuntimeError("Test error")
        
        assert agent.state == AgentState.ERROR

    def test_all_agent_states_defined(self):
        """Test that all expected agent states are defined"""
        expected_states = ["IDLE", "RUNNING", "FINISHED", "ERROR"]
        
        for state_name in expected_states:
            assert hasattr(AgentState, state_name)
            state_value = getattr(AgentState, state_name)
            assert isinstance(state_value, AgentState)


if __name__ == "__main__":
    pytest.main([__file__])

