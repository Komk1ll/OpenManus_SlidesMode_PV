"""Comprehensive tests for ToolCallAgent.

This module contains unit and integration tests for the ToolCallAgent class,
covering all major functionality including tool execution, LLM interaction,
error handling, and special tool management.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Any, Dict, List, Optional

from app.agent.toolcall import ToolCallAgent
from app.agent.base import AgentState
from app.schema import Message, ToolCall, ToolChoice, Memory, Function
from app.tool.tool_collection import ToolCollection
from app.tool.create_chat_completion import CreateChatCompletion
from app.tool.terminate import Terminate
from app.exceptions import TokenLimitExceeded
from app.llm import LLM


class MockTool:
    """Mock tool for testing purposes."""
    
    def __init__(self, name: str, result: Any = "Mock result", should_fail: bool = False):
        self.name = name
        self.result = result
        self.should_fail = should_fail
        self.call_count = 0
        self.last_args = None
    
    async def execute(self, **kwargs) -> Any:
        self.call_count += 1
        self.last_args = kwargs
        if self.should_fail:
            raise RuntimeError(f"Mock tool {self.name} failed")
        return self.result
    
    async def cleanup(self):
        """Mock cleanup method."""
        pass


class MockToolResult:
    """Mock tool result with base64_image support."""
    
    def __init__(self, content: str, base64_image: Optional[str] = None):
        self.content = content
        self.base64_image = base64_image
    
    def __str__(self):
        return self.content


class MockLLMResponse:
    """Mock LLM response for testing."""
    
    def __init__(self, content: str = "", tool_calls: Optional[List[ToolCall]] = None):
        self.content = content
        self.tool_calls = tool_calls or []


# MockMemory removed - using real Memory() instance instead


# MockLLM removed - using @patch for LLM.ask_tool instead


@pytest.fixture
def memory():
    """Create a real memory instance."""
    return Memory()


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response for patching."""
    return MockLLMResponse()


@pytest.fixture
def mock_tool_collection():
    """Create a mock tool collection."""
    collection = Mock(spec=ToolCollection)
    collection.tool_map = {
        "test_tool": MockTool("test_tool"),
        "failing_tool": MockTool("failing_tool", should_fail=True),
        "image_tool": MockTool("image_tool", MockToolResult("Image created", "base64_image_data"))
    }
    collection.to_params = Mock(return_value=[])
    
    async def mock_execute(name: str, tool_input: Dict[str, Any]):
        if name in collection.tool_map:
            return await collection.tool_map[name].execute(**tool_input)
        raise KeyError(f"Tool {name} not found")
    
    collection.execute = mock_execute
    return collection


@pytest.fixture
def basic_agent(memory, mock_tool_collection):
    """Create a basic ToolCallAgent for testing."""
    with patch('app.llm.LLM') as mock_llm_class:
        mock_llm_instance = Mock(spec=LLM)
        mock_llm_class.return_value = mock_llm_instance
        
        agent = ToolCallAgent(
            name="TestAgent",
            description="Test agent for unit tests",
            memory=memory,
            llm=mock_llm_instance,
            available_tools=mock_tool_collection,
            tool_choices="auto",
            special_tool_names=["terminate"]
        )
        
        # Store mock for easy access in tests
        agent._mock_llm = mock_llm_instance
        return agent


class TestToolCallAgentInitialization:
    """Test ToolCallAgent initialization and configuration."""
    
    def test_agent_initialization(self, memory, mock_tool_collection):
        """Test basic agent initialization."""
        with patch('app.llm.LLM') as mock_llm_class:
            mock_llm_instance = Mock(spec=LLM)
            mock_llm_class.return_value = mock_llm_instance
            
            agent = ToolCallAgent(
                name="TestAgent",
                description="Test description",
                memory=memory,
                llm=mock_llm_instance,
                available_tools=mock_tool_collection,
                tool_choices="required",
                special_tool_names=["terminate", "finish"]
            )
            
            assert agent.name == "TestAgent"
            assert agent.description == "Test description"
            assert agent.memory == memory
            assert agent.llm == mock_llm_instance
            assert agent.available_tools == mock_tool_collection
            assert agent.tool_choices == "required"
            assert agent.special_tool_names == ["terminate", "finish"]
            assert agent.state == AgentState.IDLE
    
    def test_agent_with_default_tools(self, memory):
        """Test agent initialization with default tools."""
        with patch('app.llm.LLM') as mock_llm_class:
            mock_llm_instance = Mock(spec=LLM)
            mock_llm_class.return_value = mock_llm_instance
            
            agent = ToolCallAgent(
                name="TestAgent",
                description="Test description",
                memory=memory,
                llm=mock_llm_instance
            )
            
            # Should have default tools
            assert isinstance(agent.available_tools, ToolCollection)
            assert "CreateChatCompletion" in [tool.__class__.__name__ for tool in agent.available_tools.tool_map.values()]
            assert "Terminate" in [tool.__class__.__name__ for tool in agent.available_tools.tool_map.values()]


class TestThinkMethod:
    """Test the think() method with various scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool_choice,has_tool_calls,expected_result", [
        ("auto", True, True),
        ("auto", False, False),
        ("required", True, True),
        ("required", False, True),
        ("none", False, True),
        ("none", True, True),  # Should warn but continue
    ])
    async def test_think_with_different_tool_choices(self, basic_agent, tool_choice, has_tool_calls, expected_result):
        """Test think method with different tool choice configurations."""
        basic_agent.tool_choices = tool_choice
        
        # Mock tool calls
        tool_calls = []
        if has_tool_calls:
            tool_calls = [
                ToolCall(
                    id="call_1",
                    function=Function(name="test_tool", arguments='{"arg1": "value1"}')
                )
            ]
        
        # Mock LLM response
        mock_response = MockLLMResponse(
            content="Test response",
            tool_calls=tool_calls
        )
        
        # Mock the ask_tool method
        basic_agent._mock_llm.ask_tool = AsyncMock(return_value=mock_response)
        
        result = await basic_agent.think()
        
        assert result == expected_result
        assert basic_agent.tool_calls == tool_calls
        # Check that message was added to memory
        assert len(basic_agent.memory.messages) > 0
    
    @pytest.mark.asyncio
    async def test_think_with_token_limit_exceeded(self, basic_agent):
        """Test think method handling TokenLimitExceeded error."""
        # Mock RetryError with TokenLimitExceeded as cause
        token_error = TokenLimitExceeded("Token limit exceeded")
        retry_error = Exception("Retry failed")
        retry_error.__cause__ = token_error
        
        # Mock ask_tool to raise the retry error
        basic_agent._mock_llm.ask_tool = AsyncMock(side_effect=retry_error)
        
        result = await basic_agent.think()
        
        assert result is False
        assert basic_agent.state == AgentState.FINISHED
        assert len(basic_agent.memory.messages) > 0
    
    @pytest.mark.asyncio
    async def test_think_with_no_response(self, basic_agent):
        """Test think method when LLM returns None."""
        # Mock ask_tool to return None
        basic_agent._mock_llm.ask_tool = AsyncMock(return_value=None)
        
        result = await basic_agent.think()
        
        assert result is False
        assert len(basic_agent.memory.messages) > 0
    
    @pytest.mark.asyncio
    async def test_think_with_general_exception(self, basic_agent):
        """Test think method handling general exceptions."""
        # Mock ask_tool to raise ValueError
        basic_agent._mock_llm.ask_tool = AsyncMock(side_effect=ValueError("Test error"))
        
        with pytest.raises(ValueError):
            await basic_agent.think()


class TestActMethod:
    """Test the act() method and tool execution."""
    
    @pytest.mark.asyncio
    async def test_act_with_tool_calls(self, basic_agent):
        """Test act method with valid tool calls."""
        # Setup tool calls
        basic_agent.tool_calls = [
            ToolCall(
                id="call_1",
                function=Function(name="test_tool", arguments='{"arg1": "value1"}')
            )
        ]
        
        result = await basic_agent.act()
        
        assert "Mock result" in result
        # Check that message was added to memory
        assert len(basic_agent.memory.messages) > 0
    
    @pytest.mark.asyncio
    async def test_act_without_tool_calls_required_mode(self, basic_agent):
        """Test act method without tool calls in REQUIRED mode."""
        basic_agent.tool_choices = "required"
        basic_agent.tool_calls = []
        
        with pytest.raises(ValueError, match="Tool call is required"):
            await basic_agent.act()
    
    @pytest.mark.asyncio
    async def test_act_without_tool_calls_auto_mode(self, basic_agent):
        """Test act method without tool calls in AUTO mode."""
        basic_agent.tool_choices = "auto"
        basic_agent.tool_calls = []
        # Add a message to memory
        basic_agent.memory.add_message(Message(role="assistant", content="Test content"))
        
        result = await basic_agent.act()
        
        assert "Test content" in result
    
    @pytest.mark.asyncio
    async def test_act_with_max_observe_limit(self, basic_agent):
        """Test act method with max_observe limit."""
        basic_agent.max_observe = 10
        basic_agent.tool_calls = [
            ToolCall(
                id="call_1",
                function=Function(name="test_tool", arguments='{}')
            )
        ]
        
        # Mock tool with long result
        long_result = "x" * 100
        basic_agent.available_tools.tool_map["test_tool"].result = long_result
        
        result = await basic_agent.act()
        
        # Result should be truncated
        assert len(result.split("\n\n")[0]) <= basic_agent.max_observe + 50  # Some buffer for formatting


class TestExecuteToolMethod:
    """Test the execute_tool() method."""
    
    @pytest.mark.asyncio
    async def test_execute_tool_success(self, basic_agent):
        """Test successful tool execution."""
        tool_call = ToolCall(
            id="call_1",
            function=Function(name="test_tool", arguments='{"arg1": "value1"}')
        )
        
        result = await basic_agent.execute_tool(tool_call)
        
        assert "Mock result" in result
        assert "test_tool" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_invalid_json(self, basic_agent):
        """Test tool execution with invalid JSON arguments."""
        tool_call = ToolCall(
            id="call_1",
            function=Function(name="test_tool", arguments='invalid json')
        )
        
        result = await basic_agent.execute_tool(tool_call)
        
        assert "Error parsing arguments" in result
        assert "Invalid JSON format" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_unknown_tool(self, basic_agent):
        """Test execution of unknown tool."""
        tool_call = ToolCall(
            id="call_1",
            function=Function(name="unknown_tool", arguments='{}')
        )
        
        result = await basic_agent.execute_tool(tool_call)
        
        assert "Error: Unknown tool 'unknown_tool'" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_exception(self, basic_agent):
        """Test tool execution that raises an exception."""
        tool_call = ToolCall(
            id="call_1",
            function=Function(name="failing_tool", arguments='{}')
        )
        
        result = await basic_agent.execute_tool(tool_call)
        
        assert "Error:" in result
        assert "failing_tool" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_base64_image(self, basic_agent):
        """Test tool execution that returns base64 image."""
        tool_call = ToolCall(
            id="call_1",
            function=Function(name="image_tool", arguments='{}')
        )
        
        result = await basic_agent.execute_tool(tool_call)
        
        assert "Image created" in result
        assert basic_agent._current_base64_image == "base64_image_data"
    
    @pytest.mark.asyncio
    async def test_execute_tool_invalid_command(self, basic_agent):
        """Test execution with invalid command format."""
        # Test with None command
        result = await basic_agent.execute_tool(None)
        assert "Error: Invalid command format" in result
        
        # Test with command without function
        invalid_call = ToolCall(id="call_1", function=Function(name="", arguments="{}"))
        result = await basic_agent.execute_tool(invalid_call)
        assert "Error: Invalid command format" in result


class TestSpecialToolHandling:
    """Test special tool handling methods."""
    
    @pytest.mark.asyncio
    async def test_handle_special_tool(self, basic_agent):
        """Test special tool handling."""
        # Test with special tool
        await basic_agent._handle_special_tool("terminate", "result")
        assert basic_agent.state == AgentState.FINISHED
        
        # Reset state
        basic_agent.state = AgentState.IDLE
        
        # Test with non-special tool
        await basic_agent._handle_special_tool("regular_tool", "result")
        assert basic_agent.state == AgentState.IDLE
    
    def test_is_special_tool(self, basic_agent):
        """Test special tool identification."""
        assert basic_agent._is_special_tool("terminate") is True
        assert basic_agent._is_special_tool("TERMINATE") is True  # Case insensitive
        assert basic_agent._is_special_tool("regular_tool") is False
    
    def test_should_finish_execution(self, basic_agent):
        """Test finish execution logic."""
        # Static method always returns True
        assert basic_agent._should_finish_execution() is True
        assert basic_agent._should_finish_execution(name="test", result="result") is True


class TestCleanupMethod:
    """Test the cleanup() method."""
    
    @pytest.mark.asyncio
    async def test_cleanup_success(self, basic_agent):
        """Test successful cleanup of tools."""
        # Add cleanup method to mock tools
        for tool in basic_agent.available_tools.tool_map.values():
            tool.cleanup = AsyncMock()
        
        await basic_agent.cleanup()
        
        # Verify cleanup was called on all tools
        for tool in basic_agent.available_tools.tool_map.values():
            tool.cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_with_exception(self, basic_agent):
        """Test cleanup when a tool raises an exception."""
        # Make one tool fail during cleanup
        failing_tool = basic_agent.available_tools.tool_map["test_tool"]
        failing_tool.cleanup = AsyncMock(side_effect=RuntimeError("Cleanup failed"))
        
        # Other tools should still be cleaned up
        for name, tool in basic_agent.available_tools.tool_map.items():
            if name != "test_tool":
                tool.cleanup = AsyncMock()
        
        # Should not raise exception
        await basic_agent.cleanup()
        
        # Verify other tools were still cleaned up
        for name, tool in basic_agent.available_tools.tool_map.items():
            if name != "test_tool":
                tool.cleanup.assert_called_once()


class TestRunMethod:
    """Test the run() method with cleanup."""
    
    @pytest.mark.asyncio
    async def test_run_with_cleanup(self, basic_agent):
        """Test that run method calls cleanup even on success."""
        # Mock the parent run method
        with patch.object(basic_agent.__class__.__bases__[0], 'run', new_callable=AsyncMock) as mock_super_run:
            mock_super_run.return_value = "Success"
            
            # Mock cleanup
            basic_agent.cleanup = AsyncMock()
            
            result = await basic_agent.run("test request")
            
            assert result == "Success"
            mock_super_run.assert_called_once_with("test request")
            basic_agent.cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_with_cleanup_on_exception(self, basic_agent):
        """Test that run method calls cleanup even when parent run fails."""
        # Mock the parent run method to raise exception
        with patch.object(basic_agent.__class__.__bases__[0], 'run', new_callable=AsyncMock) as mock_super_run:
            mock_super_run.side_effect = RuntimeError("Run failed")
            
            # Mock cleanup
            basic_agent.cleanup = AsyncMock()
            
            with pytest.raises(RuntimeError, match="Run failed"):
                await basic_agent.run("test request")
            
            mock_super_run.assert_called_once_with("test request")
            basic_agent.cleanup.assert_called_once()


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_think_act_cycle(self, basic_agent):
        """Test complete think-act cycle."""
        # Setup LLM response with tool call
        tool_calls = [
            ToolCall(
                id="call_1",
                function=Function(name="test_tool", arguments='{"arg1": "value1"}')
            )
        ]
        mock_response = MockLLMResponse(
            content="I'll use the test tool",
            tool_calls=tool_calls
        )
        basic_agent.llm.create_chat_completion.return_value = mock_response
        
        # Execute think
        think_result = await basic_agent.think()
        assert think_result is True
        assert len(basic_agent.tool_calls) == 1
        
        # Execute act
        act_result = await basic_agent.act()
        assert "Mock result" in act_result
        
        # Verify memory interactions
        assert basic_agent.memory.add_message.call_count >= 2  # Assistant message + tool message
    
    @pytest.mark.asyncio
    async def test_special_tool_workflow(self, basic_agent):
        """Test workflow with special tool that finishes execution."""
        # Add terminate tool to collection
        basic_agent.available_tools.tool_map["terminate"] = MockTool("terminate", "Task completed")
        
        # Setup tool call for terminate
        tool_calls = [
            ToolCall(
                id="call_1",
                function=Function(name="terminate", arguments='{"reason": "Task completed"}')
            )
        ]
        mock_response = MockLLMResponse(
            content="Task is complete",
            tool_calls=tool_calls
        )
        basic_agent.llm.create_chat_completion.return_value = mock_response
        
        # Execute think and act
        await basic_agent.think()
        await basic_agent.act()
        
        # Agent should be finished
        assert basic_agent.state == AgentState.FINISHED
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, basic_agent):
        """Test error handling and recovery."""
        # Setup tool call that will fail
        tool_calls = [
            ToolCall(
                id="call_1",
                function=Function(name="failing_tool", arguments='{}')
            )
        ]
        mock_response = MockLLMResponse(
            content="I'll try the failing tool",
            tool_calls=tool_calls
        )
        basic_agent.llm.create_chat_completion.return_value = mock_response
        
        # Execute workflow
        await basic_agent.think()
        result = await basic_agent.act()
        
        # Should handle error gracefully
        assert "Error:" in result
        assert "failing_tool" in result
        assert basic_agent.state != AgentState.FINISHED  # Should not finish on tool error


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    async def test_empty_tool_arguments(self, basic_agent):
        """Test tool execution with empty arguments."""
        tool_call = ToolCall(
            id="call_1",
            function=Function(name="test_tool", arguments='')
        )
        
        result = await basic_agent.execute_tool(tool_call)
        
        # Should handle empty arguments as empty dict
        assert "Mock result" in result
    
    @pytest.mark.asyncio
    async def test_none_tool_arguments(self, basic_agent):
        """Test tool execution with None arguments."""
        tool_call = ToolCall(
            id="call_1",
            function=Function(name="test_tool", arguments="")
        )
        
        result = await basic_agent.execute_tool(tool_call)
        
        # Should handle None arguments as empty dict
        assert "Mock result" in result
    
    @pytest.mark.asyncio
    async def test_multiple_tool_calls_with_mixed_results(self, basic_agent):
        """Test multiple tool calls with some succeeding and some failing."""
        basic_agent.tool_calls = [
            ToolCall(
                id="call_1",
                function=Function(name="test_tool", arguments='{}')
            ),
            ToolCall(
                id="call_2",
                function=Function(name="failing_tool", arguments='{}')
            ),
            ToolCall(
                id="call_3",
                function=Function(name="test_tool", arguments='{}')
            )
        ]
        
        result = await basic_agent.act()
        
        # Should contain results from all tools
        results = result.split("\n\n")
        assert len(results) == 3
        assert "Mock result" in results[0]
        assert "Error:" in results[1]
        assert "Mock result" in results[2]
    
    @pytest.mark.asyncio
    async def test_tool_with_no_output(self, basic_agent):
        """Test tool that returns None or empty result."""
        # Add tool that returns None
        basic_agent.available_tools.tool_map["empty_tool"] = MockTool("empty_tool", None)
        
        tool_call = ToolCall(
            id="call_1",
            function=Function(name="empty_tool", arguments='{}')
        )
        
        result = await basic_agent.execute_tool(tool_call)
        
        assert "completed with no output" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])