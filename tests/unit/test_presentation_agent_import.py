"""
Unit test for presentation_agent import fix
Tests that the corrected import from app.tool.base works properly
"""

import pytest
from unittest.mock import Mock, patch


class TestPresentationAgentImport:
    """Test cases for presentation agent import fix"""

    def test_tool_result_import_success(self):
        """Test that ToolResult can be imported from app.tool.base"""
        try:
            from app.tool.base import ToolResult
            assert ToolResult is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ToolResult from app.tool.base: {e}")

    def test_presentation_agent_import_success(self):
        """Test that presentation_agent can be imported without errors"""
        try:
            from app.agent.presentation_agent import PresentationAgent
            assert PresentationAgent is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PresentationAgent: {e}")

    def test_presentation_agent_uses_correct_tool_result(self):
        """Test that presentation_agent uses ToolResult from correct module"""
        from app.agent.presentation_agent import ToolResult as AgentToolResult
        from app.tool.base import ToolResult as BaseToolResult
        
        # They should be the same class
        assert AgentToolResult is BaseToolResult

    def test_tool_result_functionality_in_presentation_agent(self):
        """Test that ToolResult works correctly in presentation agent context"""
        from app.tool.base import ToolResult
        
        # Test basic ToolResult functionality
        result = ToolResult(output="Test output")
        assert result.output == "Test output"
        assert result.error is None
        
        # Test with error
        error_result = ToolResult(error="Test error")
        assert error_result.error == "Test error"
        assert str(error_result) == "Error: Test error"

    def test_presentation_agent_can_create_tool_results(self):
        """Test that presentation agent can create and use ToolResult instances"""
        # Mock the dependencies to avoid complex setup
        with patch('app.agent.presentation_agent.GenerateStructureTool'), \
             patch('app.agent.presentation_agent.GenerateSlideContentTool'), \
             patch('app.agent.presentation_agent.SearchImageTool'), \
             patch('app.agent.presentation_agent.ExportPresentationTool'):
            
            from app.agent.presentation_agent import PresentationAgent, ToolResult
            
            # Test that we can create a ToolResult in the same context
            result = ToolResult(output="Presentation created successfully")
            assert result.output == "Presentation created successfully"
            assert bool(result) is True

    def test_no_core_base_tool_import(self):
        """Test that app.core.base_tool import is not used"""
        import ast
        import inspect
        
        # Get the source code of presentation_agent
        from app.agent import presentation_agent
        source = inspect.getsource(presentation_agent)
        
        # Parse the AST to check imports
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "app.core.base_tool":
                    pytest.fail("Found import from app.core.base_tool - should be app.tool.base")

    def test_import_structure_consistency(self):
        """Test that the import structure is consistent"""
        # Test that both modules exist and have ToolResult
        from app.tool.base import ToolResult as ToolResultBase
        
        # Verify ToolResult has expected attributes
        assert hasattr(ToolResultBase, 'output')
        assert hasattr(ToolResultBase, 'error')
        assert hasattr(ToolResultBase, 'base64_image')
        assert hasattr(ToolResultBase, 'system')

    @patch('app.agent.presentation_agent.logging')
    def test_presentation_agent_module_loads_completely(self, mock_logging):
        """Test that the entire presentation_agent module loads without issues"""
        try:
            import app.agent.presentation_agent
            # If we get here, the module loaded successfully
            assert True
        except Exception as e:
            pytest.fail(f"presentation_agent module failed to load: {e}")

    def test_tool_result_inheritance_chain(self):
        """Test that ToolResult maintains proper inheritance"""
        from app.tool.base import ToolResult, CLIResult, ToolFailure
        
        # Test inheritance relationships
        cli_result = CLIResult(output="CLI output")
        tool_failure = ToolFailure(error="Failure")
        
        assert isinstance(cli_result, ToolResult)
        assert isinstance(tool_failure, ToolResult)

    def test_presentation_config_dataclass(self):
        """Test that PresentationConfig can be imported and used"""
        try:
            from app.agent.presentation_agent import PresentationConfig
            
            config = PresentationConfig(
                topic="Test Presentation",
                slide_count=5,
                language="english"
            )
            
            assert config.topic == "Test Presentation"
            assert config.slide_count == 5
            assert config.language == "english"
            
        except ImportError as e:
            pytest.fail(f"Failed to import PresentationConfig: {e}")


if __name__ == "__main__":
    pytest.main([__file__])

