"""Unit tests for base tool classes."""

import pytest
from unittest.mock import Mock
from typing import Any, Dict

from app.tool.base import BaseTool, ToolResult, CLIResult, ToolFailure


class TestToolResult:
    """Test cases for ToolResult class."""

    def test_tool_result_creation(self) -> None:
        """Test ToolResult creation with different parameters."""
        result = ToolResult(output="test output", error=None)
        assert result.output == "test output"
        assert result.error is None
        assert result.base64_image is None
        assert result.system is None

    def test_tool_result_with_error(self) -> None:
        """Test ToolResult with error."""
        result = ToolResult(output=None, error="test error")
        assert result.output is None
        assert result.error == "test error"

    def test_tool_result_with_image(self) -> None:
        """Test ToolResult with base64 image."""
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        result = ToolResult(output="image result", base64_image=image_data)
        assert result.base64_image == image_data

    def test_tool_result_bool_conversion(self) -> None:
        """Test ToolResult boolean conversion."""
        # Empty result should be False
        empty_result = ToolResult()
        assert not bool(empty_result)
        
        # Result with output should be True
        result_with_output = ToolResult(output="something")
        assert bool(result_with_output)
        
        # Result with error should be True
        result_with_error = ToolResult(error="error")
        assert bool(result_with_error)

    def test_tool_result_string_conversion(self) -> None:
        """Test ToolResult string conversion."""
        # Result with error shows error
        error_result = ToolResult(error="test error")
        assert str(error_result) == "Error: test error"
        
        # Result without error shows output
        output_result = ToolResult(output="test output")
        assert str(output_result) == "test output"

    def test_tool_result_addition(self) -> None:
        """Test ToolResult addition operator."""
        result1 = ToolResult(output="part1", error=None)
        result2 = ToolResult(output="part2", error=None)
        
        combined = result1 + result2
        assert combined.output == "part1part2"
        assert combined.error is None

    def test_tool_result_addition_with_errors(self) -> None:
        """Test ToolResult addition with errors."""
        result1 = ToolResult(error="error1")
        result2 = ToolResult(error="error2")
        
        combined = result1 + result2
        assert combined.error == "error1error2"

    def test_tool_result_addition_conflicting_images(self) -> None:
        """Test ToolResult addition with conflicting images raises error."""
        result1 = ToolResult(base64_image="image1")
        result2 = ToolResult(base64_image="image2")
        
        with pytest.raises(ValueError, match="Cannot combine tool results"):
            result1 + result2

    def test_tool_result_replace(self) -> None:
        """Test ToolResult replace method."""
        original = ToolResult(output="original", error="original_error")
        modified = original.replace(output="new_output")
        
        assert modified.output == "new_output"
        assert modified.error == "original_error"  # Unchanged
        assert original.output == "original"  # Original unchanged


class TestCLIResult:
    """Test cases for CLIResult class."""

    def test_cli_result_inheritance(self) -> None:
        """Test that CLIResult inherits from ToolResult."""
        cli_result = CLIResult(output="CLI output")
        assert isinstance(cli_result, ToolResult)
        assert cli_result.output == "CLI output"


class TestToolFailure:
    """Test cases for ToolFailure class."""

    def test_tool_failure_inheritance(self) -> None:
        """Test that ToolFailure inherits from ToolResult."""
        failure = ToolFailure(error="Tool failed")
        assert isinstance(failure, ToolResult)
        assert failure.error == "Tool failed"


class MockTool(BaseTool):
    """Mock tool for testing BaseTool functionality."""
    
    name: str = "mock_tool"
    description: str = "A mock tool for testing"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Test message"}
        },
        "required": ["message"]
    }

    async def execute(self, **kwargs: Any) -> str:
        """Execute the mock tool."""
        message = kwargs.get("message", "default")
        return f"Mock tool executed with: {message}"


class TestBaseTool:
    """Test cases for BaseTool class."""

    def test_base_tool_creation(self) -> None:
        """Test BaseTool creation with required fields."""
        tool = MockTool()
        assert tool.name == "mock_tool"
        assert tool.description == "A mock tool for testing"
        assert tool.parameters is not None

    def test_to_param_method(self) -> None:
        """Test to_param method returns correct format."""
        tool = MockTool()
        param = tool.to_param()
        
        assert param["type"] == "function"
        assert param["function"]["name"] == "mock_tool"
        assert param["function"]["description"] == "A mock tool for testing"
        assert param["function"]["parameters"] == tool.parameters

    @pytest.mark.asyncio
    async def test_tool_call_operator(self) -> None:
        """Test __call__ operator delegates to execute."""
        tool = MockTool()
        result = await tool(message="test message")
        assert result == "Mock tool executed with: test message"

    @pytest.mark.asyncio
    async def test_tool_execute_method(self) -> None:
        """Test execute method directly."""
        tool = MockTool()
        result = await tool.execute(message="direct test")
        assert result == "Mock tool executed with: direct test"

    @pytest.mark.asyncio
    async def test_tool_execute_with_default_params(self) -> None:
        """Test execute method with default parameters."""
        tool = MockTool()
        result = await tool.execute()
        assert result == "Mock tool executed with: default"

    def test_tool_parameters_validation(self) -> None:
        """Test tool parameter validation."""
        tool = MockTool()
        params = tool.parameters
        
        assert params["type"] == "object"
        assert "properties" in params
        assert "message" in params["properties"]
        assert params["properties"]["message"]["type"] == "string"
        assert "required" in params


class AsyncErrorTool(BaseTool):
    """Mock tool that raises exceptions for testing."""
    
    name: str = "error_tool"
    description: str = "A tool that raises errors"
    
    async def execute(self, **kwargs: Any) -> str:
        """Execute and raise an error."""
        raise ValueError("Simulated tool error")


class TestBaseToolErrorHandling:
    """Test error handling in BaseTool."""

    @pytest.mark.asyncio
    async def test_tool_exception_propagation(self) -> None:
        """Test that tool exceptions are properly propagated."""
        error_tool = AsyncErrorTool()
        
        with pytest.raises(ValueError, match="Simulated tool error"):
            await error_tool.execute()

    @pytest.mark.asyncio
    async def test_tool_call_exception_propagation(self) -> None:
        """Test that exceptions are propagated through __call__."""
        error_tool = AsyncErrorTool()
        
        with pytest.raises(ValueError, match="Simulated tool error"):
            await error_tool()


class TestToolResultEdgeCases:
    """Test edge cases for ToolResult."""

    def test_tool_result_none_values(self) -> None:
        """Test ToolResult with None values."""
        result = ToolResult(output=None, error=None, base64_image=None, system=None)
        assert not bool(result)  # Should be False when all fields are None
        assert str(result) == ""  # Should handle None output gracefully

    def test_tool_result_empty_string_output(self) -> None:
        """Test ToolResult with empty string output."""
        result = ToolResult(output="")
        assert not bool(result)  # Empty string should be False
        assert str(result) == ""

    def test_tool_result_zero_output(self) -> None:
        """Test ToolResult with zero as output."""
        result = ToolResult(output=0)
        assert not bool(result)  # Zero should be False
        assert str(result) == "0"

    def test_tool_result_addition_partial_none(self) -> None:
        """Test ToolResult addition when one has None values."""
        result1 = ToolResult(output="text")
        result2 = ToolResult(output=None, error="error")
        
        combined = result1 + result2
        assert combined.output == "text"
        assert combined.error == "error"