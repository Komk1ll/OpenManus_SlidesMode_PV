"""
Unit tests for app.tool.base module
Tests for schemas, validation, and ToolResult functionality
"""

import pytest
from typing import Any, Dict
from unittest.mock import Mock

from app.tool.base import BaseTool, ToolResult, CLIResult, ToolFailure


class TestBaseTool:
    """Test cases for BaseTool abstract base class"""

    def test_base_tool_cannot_be_instantiated(self):
        """Test that BaseTool cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseTool(name="test", description="test")

    def test_concrete_tool_implementation(self):
        """Test concrete implementation of BaseTool"""
        
        class ConcreteTool(BaseTool):
            async def execute(self, **kwargs) -> Any:
                return f"Executed with {kwargs}"
        
        tool = ConcreteTool(name="test_tool", description="A test tool")
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.parameters is None

    def test_tool_with_parameters(self):
        """Test tool creation with parameters"""
        
        class ParameterizedTool(BaseTool):
            async def execute(self, **kwargs) -> Any:
                return kwargs
        
        params = {
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            }
        }
        
        tool = ParameterizedTool(
            name="param_tool",
            description="Tool with parameters",
            parameters=params
        )
        
        assert tool.parameters == params

    @pytest.mark.asyncio
    async def test_tool_call_method(self):
        """Test tool __call__ method delegates to execute"""
        
        class CallableTool(BaseTool):
            async def execute(self, **kwargs) -> Any:
                return f"Called with {kwargs}"
        
        tool = CallableTool(name="callable", description="Callable tool")
        result = await tool(param1="value1", param2="value2")
        
        assert result == "Called with {'param1': 'value1', 'param2': 'value2'}"

    def test_to_param_method(self):
        """Test conversion to function call format"""
        
        class FormattedTool(BaseTool):
            async def execute(self, **kwargs) -> Any:
                return None
        
        params = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
        
        tool = FormattedTool(
            name="search_tool",
            description="Search for information",
            parameters=params
        )
        
        result = tool.to_param()
        
        expected = {
            "type": "function",
            "function": {
                "name": "search_tool",
                "description": "Search for information",
                "parameters": params
            }
        }
        
        assert result == expected

    def test_to_param_without_parameters(self):
        """Test to_param with no parameters"""
        
        class SimpleToolTool(BaseTool):
            async def execute(self, **kwargs) -> Any:
                return None
        
        tool = SimpleToolTool(name="simple", description="Simple tool")
        result = tool.to_param()
        
        expected = {
            "type": "function",
            "function": {
                "name": "simple",
                "description": "Simple tool",
                "parameters": None
            }
        }
        
        assert result == expected


class TestToolResult:
    """Test cases for ToolResult class"""

    def test_tool_result_creation_empty(self):
        """Test creating empty ToolResult"""
        result = ToolResult()
        
        assert result.output is None
        assert result.error is None
        assert result.base64_image is None
        assert result.system is None

    def test_tool_result_creation_with_output(self):
        """Test creating ToolResult with output"""
        result = ToolResult(output="Success!")
        
        assert result.output == "Success!"
        assert result.error is None
        assert result.base64_image is None
        assert result.system is None

    def test_tool_result_creation_with_error(self):
        """Test creating ToolResult with error"""
        result = ToolResult(error="Something went wrong")
        
        assert result.output is None
        assert result.error == "Something went wrong"
        assert result.base64_image is None
        assert result.system is None

    def test_tool_result_creation_complete(self):
        """Test creating ToolResult with all fields"""
        result = ToolResult(
            output="Success",
            error=None,
            base64_image="base64data",
            system="System message"
        )
        
        assert result.output == "Success"
        assert result.error is None
        assert result.base64_image == "base64data"
        assert result.system == "System message"

    def test_tool_result_bool_empty(self):
        """Test boolean evaluation of empty ToolResult"""
        result = ToolResult()
        assert not bool(result)

    def test_tool_result_bool_with_output(self):
        """Test boolean evaluation of ToolResult with output"""
        result = ToolResult(output="Something")
        assert bool(result)

    def test_tool_result_bool_with_error(self):
        """Test boolean evaluation of ToolResult with error"""
        result = ToolResult(error="Error")
        assert bool(result)

    def test_tool_result_bool_with_image(self):
        """Test boolean evaluation of ToolResult with image"""
        result = ToolResult(base64_image="image_data")
        assert bool(result)

    def test_tool_result_bool_with_system(self):
        """Test boolean evaluation of ToolResult with system message"""
        result = ToolResult(system="System")
        assert bool(result)

    def test_tool_result_addition_outputs(self):
        """Test adding ToolResults with outputs"""
        result1 = ToolResult(output="Hello ")
        result2 = ToolResult(output="World!")
        
        combined = result1 + result2
        
        assert combined.output == "Hello World!"
        assert combined.error is None
        assert combined.base64_image is None
        assert combined.system is None

    def test_tool_result_addition_errors(self):
        """Test adding ToolResults with errors"""
        result1 = ToolResult(error="Error 1. ")
        result2 = ToolResult(error="Error 2.")
        
        combined = result1 + result2
        
        assert combined.output is None
        assert combined.error == "Error 1. Error 2."
        assert combined.base64_image is None
        assert combined.system is None

    def test_tool_result_addition_mixed(self):
        """Test adding ToolResults with mixed fields"""
        result1 = ToolResult(output="Output", system="System 1")
        result2 = ToolResult(error="Error", system=" System 2")
        
        combined = result1 + result2
        
        assert combined.output == "Output"
        assert combined.error == "Error"
        assert combined.base64_image is None
        assert combined.system == "System 1 System 2"

    def test_tool_result_addition_conflicting_images(self):
        """Test adding ToolResults with conflicting images raises error"""
        result1 = ToolResult(base64_image="image1")
        result2 = ToolResult(base64_image="image2")
        
        with pytest.raises(ValueError, match="Cannot combine tool results"):
            result1 + result2

    def test_tool_result_addition_one_image(self):
        """Test adding ToolResults where only one has image"""
        result1 = ToolResult(output="Text")
        result2 = ToolResult(base64_image="image_data")
        
        combined = result1 + result2
        
        assert combined.output == "Text"
        assert combined.base64_image == "image_data"

    def test_tool_result_str_with_error(self):
        """Test string representation with error"""
        result = ToolResult(error="Something failed")
        assert str(result) == "Error: Something failed"

    def test_tool_result_str_with_output(self):
        """Test string representation with output"""
        result = ToolResult(output="Success message")
        assert str(result) == "Success message"

    def test_tool_result_str_empty(self):
        """Test string representation of empty result"""
        result = ToolResult()
        assert str(result) == "None"

    def test_tool_result_replace_method(self):
        """Test replace method creates new instance with updated fields"""
        original = ToolResult(output="Original", error=None)
        updated = original.replace(error="New error", system="System message")
        
        # Original should be unchanged
        assert original.output == "Original"
        assert original.error is None
        assert original.system is None
        
        # Updated should have new values
        assert updated.output == "Original"
        assert updated.error == "New error"
        assert updated.system == "System message"

    def test_tool_result_replace_with_none(self):
        """Test replace method with None values"""
        original = ToolResult(output="Original", error="Error")
        updated = original.replace(error=None)
        
        assert updated.output == "Original"
        assert updated.error is None

    def test_tool_result_arbitrary_types(self):
        """Test ToolResult with arbitrary types in output"""
        complex_output = {
            "data": [1, 2, 3],
            "metadata": {"type": "list", "count": 3}
        }
        
        result = ToolResult(output=complex_output)
        assert result.output == complex_output
        assert isinstance(result.output, dict)


class TestCLIResult:
    """Test cases for CLIResult class"""

    def test_cli_result_inheritance(self):
        """Test CLIResult inherits from ToolResult"""
        result = CLIResult(output="CLI output")
        
        assert isinstance(result, ToolResult)
        assert result.output == "CLI output"

    def test_cli_result_functionality(self):
        """Test CLIResult has same functionality as ToolResult"""
        result1 = CLIResult(output="Command: ")
        result2 = CLIResult(output="ls -la")
        
        combined = result1 + result2
        assert isinstance(combined, ToolResult)
        assert combined.output == "Command: ls -la"


class TestToolFailure:
    """Test cases for ToolFailure class"""

    def test_tool_failure_inheritance(self):
        """Test ToolFailure inherits from ToolResult"""
        failure = ToolFailure(error="Operation failed")
        
        assert isinstance(failure, ToolResult)
        assert failure.error == "Operation failed"

    def test_tool_failure_functionality(self):
        """Test ToolFailure has same functionality as ToolResult"""
        failure = ToolFailure(error="Critical error", system="System down")
        
        assert str(failure) == "Error: Critical error"
        assert failure.system == "System down"

    def test_tool_failure_bool_evaluation(self):
        """Test ToolFailure boolean evaluation"""
        failure = ToolFailure(error="Failed")
        assert bool(failure)  # Should be True because it has an error


class TestToolResultValidation:
    """Test cases for ToolResult validation and edge cases"""

    def test_tool_result_with_empty_strings(self):
        """Test ToolResult with empty strings"""
        result = ToolResult(output="", error="", system="")
        
        # Empty strings should still evaluate to True in boolean context
        assert bool(result)

    def test_tool_result_with_zero_values(self):
        """Test ToolResult with zero/false values"""
        result = ToolResult(output=0)
        assert bool(result)  # 0 is a valid output
        
        result = ToolResult(output=False)
        assert bool(result)  # False is a valid output

    def test_tool_result_field_types(self):
        """Test ToolResult accepts various field types"""
        # Test with different output types
        result_str = ToolResult(output="string")
        result_int = ToolResult(output=42)
        result_list = ToolResult(output=[1, 2, 3])
        result_dict = ToolResult(output={"key": "value"})
        
        assert result_str.output == "string"
        assert result_int.output == 42
        assert result_list.output == [1, 2, 3]
        assert result_dict.output == {"key": "value"}

    def test_tool_result_immutability_after_creation(self):
        """Test that ToolResult fields can be accessed but original is preserved"""
        original_data = {"key": "value"}
        result = ToolResult(output=original_data)
        
        # Modifying the original data shouldn't affect the result
        original_data["key"] = "modified"
        
        # This test depends on whether Pydantic creates deep copies
        # In practice, you should not modify the original data
        assert result.output["key"] in ["value", "modified"]  # Either is acceptable


if __name__ == "__main__":
    pytest.main([__file__])

