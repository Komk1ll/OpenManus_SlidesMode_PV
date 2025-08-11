"""Unit tests for ReActAgent.

Tests cover abstract methods, step execution logic, state management,
and integration with LLM and Memory components.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Optional

from app.agent.react import ReActAgent
from app.agent.base import BaseAgent
from app.llm import LLM
from app.schema import AgentState, Memory
from app.interfaces.llm import ILLMProvider
from app.interfaces.logger import ILogger
from app.interfaces.config import IConfig
from app.interfaces.sandbox import ISandboxClient


class ConcreteReActAgent(ReActAgent):
    """Concrete implementation of ReActAgent for testing."""
    
    name: str = "test_react_agent"
    description: str = "A test ReAct agent"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._should_act = True
        self._act_result = "Action executed"
        self._think_call_count = 0
        self._act_call_count = 0
    
    async def think(self) -> bool:
        """Mock think implementation."""
        self._think_call_count += 1
        return self._should_act
    
    async def act(self) -> str:
        """Mock act implementation."""
        self._act_call_count += 1
        return self._act_result
    
    def set_think_result(self, should_act: bool):
        """Set the result of think method."""
        self._should_act = should_act
    
    def set_act_result(self, result: str):
        """Set the result of act method."""
        self._act_result = result


class ErrorReActAgent(ReActAgent):
    """ReActAgent that raises errors for testing."""
    
    name: str = "error_react_agent"
    
    async def think(self) -> bool:
        """Think method that raises an error."""
        raise ValueError("Think error")
    
    async def act(self) -> str:
        """Act method that raises an error."""
        raise RuntimeError("Act error")


class TestReActAgent:
    """Test suite for ReActAgent class."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        llm = Mock(spec=LLM)
        llm.generate = AsyncMock(return_value="LLM response")
        return llm
    
    @pytest.fixture
    def mock_memory(self):
        """Mock Memory for testing."""
        memory = Mock(spec=Memory)
        memory.add = Mock()
        memory.get_recent = Mock(return_value=[])
        return memory
    
    @pytest.fixture
    def agent(self, mock_llm, mock_memory):
        """Create ConcreteReActAgent for testing."""
        return ConcreteReActAgent(
            llm=mock_llm,
            memory=mock_memory
        )
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock dependencies for agent creation."""
        return {
            "llm_provider": Mock(spec=ILLMProvider),
            "logger": Mock(spec=ILogger),
            "config": Mock(spec=IConfig),
            "sandbox_client": Mock(spec=ISandboxClient)
        }
    
    def test_react_agent_inheritance(self):
        """Test that ReActAgent properly inherits from BaseAgent and ABC."""
        assert issubclass(ReActAgent, BaseAgent)
        
        # Test that ReActAgent is abstract
        with pytest.raises(TypeError):
            ReActAgent()
    
    def test_react_agent_abstract_methods(self):
        """Test that think and act are abstract methods."""
        # Verify abstract methods exist
        assert hasattr(ReActAgent, 'think')
        assert hasattr(ReActAgent, 'act')
        
        # Verify they are abstract
        assert getattr(ReActAgent.think, '__isabstractmethod__', False)
        assert getattr(ReActAgent.act, '__isabstractmethod__', False)
    
    def test_react_agent_default_attributes(self, agent):
        """Test default attribute values."""
        assert agent.name == "test_react_agent"
        assert agent.description == "A test ReAct agent"
        assert agent.system_prompt is None
        assert agent.next_step_prompt is None
        assert isinstance(agent.llm, LLM)
        assert isinstance(agent.memory, Memory)
        assert agent.state == AgentState.IDLE
        assert agent.max_steps == 10
        assert agent.current_step == 0
    
    def test_react_agent_custom_attributes(self, mock_llm, mock_memory):
        """Test agent creation with custom attributes."""
        custom_agent = ConcreteReActAgent(
            name="custom_agent",
            description="Custom description",
            system_prompt="Custom system prompt",
            next_step_prompt="Custom next step prompt",
            llm=mock_llm,
            memory=mock_memory,
            state=AgentState.RUNNING,
            max_steps=20,
            current_step=5
        )
        
        assert custom_agent.name == "custom_agent"
        assert custom_agent.description == "Custom description"
        assert custom_agent.system_prompt == "Custom system prompt"
        assert custom_agent.next_step_prompt == "Custom next step prompt"
        assert custom_agent.llm == mock_llm
        assert custom_agent.memory == mock_memory
        assert custom_agent.state == AgentState.RUNNING
        assert custom_agent.max_steps == 20
        assert custom_agent.current_step == 5
    
    @pytest.mark.asyncio
    async def test_step_think_and_act(self, agent):
        """Test step method when think returns True."""
        agent.set_think_result(True)
        agent.set_act_result("Test action result")
        
        result = await agent.step()
        
        assert result == "Test action result"
        assert agent._think_call_count == 1
        assert agent._act_call_count == 1
    
    @pytest.mark.asyncio
    async def test_step_think_only(self, agent):
        """Test step method when think returns False."""
        agent.set_think_result(False)
        
        result = await agent.step()
        
        assert result == "Thinking complete - no action needed"
        assert agent._think_call_count == 1
        assert agent._act_call_count == 0
    
    @pytest.mark.asyncio
    async def test_step_multiple_calls(self, agent):
        """Test multiple step calls increment counters correctly."""
        agent.set_think_result(True)
        agent.set_act_result("Action result")
        
        # Call step multiple times
        await agent.step()
        await agent.step()
        await agent.step()
        
        assert agent._think_call_count == 3
        assert agent._act_call_count == 3
    
    @pytest.mark.asyncio
    async def test_step_alternating_think_results(self, agent):
        """Test step with alternating think results."""
        results = []
        
        # First step: think returns True
        agent.set_think_result(True)
        agent.set_act_result("Action 1")
        result1 = await agent.step()
        results.append(result1)
        
        # Second step: think returns False
        agent.set_think_result(False)
        result2 = await agent.step()
        results.append(result2)
        
        # Third step: think returns True again
        agent.set_think_result(True)
        agent.set_act_result("Action 2")
        result3 = await agent.step()
        results.append(result3)
        
        assert results[0] == "Action 1"
        assert results[1] == "Thinking complete - no action needed"
        assert results[2] == "Action 2"
        assert agent._think_call_count == 3
        assert agent._act_call_count == 2  # Only called when think returns True
    
    @pytest.mark.asyncio
    async def test_think_error_handling(self):
        """Test error handling in think method."""
        error_agent = ErrorReActAgent()
        
        with pytest.raises(ValueError, match="Think error"):
            await error_agent.step()
    
    @pytest.mark.asyncio
    async def test_act_error_handling(self, agent):
        """Test error handling in act method."""
        # Mock act to raise an error
        async def failing_act():
            raise RuntimeError("Act failed")
        
        agent.act = failing_act
        agent.set_think_result(True)
        
        with pytest.raises(RuntimeError, match="Act failed"):
            await agent.step()
    
    def test_llm_integration(self, agent, mock_llm):
        """Test LLM integration."""
        assert agent.llm == mock_llm
        
        # Test LLM can be replaced
        new_llm = Mock(spec=LLM)
        agent.llm = new_llm
        assert agent.llm == new_llm
    
    def test_memory_integration(self, agent, mock_memory):
        """Test Memory integration."""
        assert agent.memory == mock_memory
        
        # Test memory can be replaced
        new_memory = Mock(spec=Memory)
        agent.memory = new_memory
        assert agent.memory == new_memory
    
    def test_state_management(self, agent):
        """Test agent state management."""
        # Initial state
        assert agent.state == AgentState.IDLE
        
        # Change state
        agent.state = AgentState.RUNNING
        assert agent.state == AgentState.RUNNING
        
        agent.state = AgentState.COMPLETED
        assert agent.state == AgentState.COMPLETED
        
        agent.state = AgentState.ERROR
        assert agent.state == AgentState.ERROR
    
    def test_step_counter(self, agent):
        """Test step counter management."""
        assert agent.current_step == 0
        assert agent.max_steps == 10
        
        # Modify step counter
        agent.current_step = 5
        assert agent.current_step == 5
        
        # Modify max steps
        agent.max_steps = 20
        assert agent.max_steps == 20
    
    @pytest.mark.asyncio
    async def test_step_with_different_act_results(self, agent):
        """Test step method with different act results."""
        agent.set_think_result(True)
        
        # Test with string result
        agent.set_act_result("String result")
        result1 = await agent.step()
        assert result1 == "String result"
        
        # Test with empty string
        agent.set_act_result("")
        result2 = await agent.step()
        assert result2 == ""
        
        # Test with multiline string
        multiline_result = "Line 1\nLine 2\nLine 3"
        agent.set_act_result(multiline_result)
        result3 = await agent.step()
        assert result3 == multiline_result
    
    def test_agent_serialization(self, agent):
        """Test that agent can be serialized/deserialized."""
        # Test model_dump
        agent_dict = agent.model_dump()
        
        assert agent_dict['name'] == "test_react_agent"
        assert agent_dict['description'] == "A test ReAct agent"
        assert agent_dict['state'] == AgentState.IDLE
        assert agent_dict['max_steps'] == 10
        assert agent_dict['current_step'] == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_step_calls(self, agent):
        """Test concurrent step calls (though not recommended in practice)."""
        import asyncio
        
        agent.set_think_result(True)
        agent.set_act_result("Concurrent result")
        
        # Run multiple steps concurrently
        tasks = [agent.step() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        
        # All should return the same result
        assert all(result == "Concurrent result" for result in results)
        
        # Think and act should be called for each step
        assert agent._think_call_count == 3
        assert agent._act_call_count == 3
    
    def test_agent_with_none_llm(self):
        """Test agent creation with None LLM."""
        agent = ConcreteReActAgent(llm=None)
        assert agent.llm is None
    
    def test_agent_field_validation(self):
        """Test Pydantic field validation."""
        # Test with invalid max_steps
        with pytest.raises(ValueError):
            ConcreteReActAgent(max_steps=-1)
        
        # Test with invalid current_step
        with pytest.raises(ValueError):
            ConcreteReActAgent(current_step=-1)
    
    @pytest.mark.asyncio
    async def test_step_inheritance_from_base_agent(self, agent):
        """Test that step method properly overrides BaseAgent.step."""
        # Verify that our step method is called, not BaseAgent.step
        result = await agent.step()
        
        # Should call our implementation, not BaseAgent's abstract step
        assert result in ["Action executed", "Thinking complete - no action needed"]
        assert agent._think_call_count == 1
    
    def test_create_with_dependencies_integration(self, mock_dependencies):
        """Test integration with create_with_dependencies pattern."""
        # This would typically be tested in integration tests,
        # but we can verify the agent accepts the expected dependencies
        
        # Mock the create_with_dependencies method
        with patch.object(ConcreteReActAgent, 'create_with_dependencies') as mock_create:
            mock_agent = ConcreteReActAgent()
            mock_create.return_value = mock_agent
            
            result = ConcreteReActAgent.create_with_dependencies(
                **mock_dependencies,
                name="test_agent"
            )
            
            mock_create.assert_called_once_with(
                **mock_dependencies,
                name="test_agent"
            )
            assert result == mock_agent