#!/usr/bin/env python3
"""
Simple test to verify the import fix works
"""

def test_direct_import():
    """Test direct import of ToolResult from base module"""
    try:
        # Import directly from the base module, bypassing __init__.py
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Import the base module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "base", 
            os.path.join(os.path.dirname(__file__), "app", "tool", "base.py")
        )
        base_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(base_module)
        
        ToolResult = base_module.ToolResult
        
        # Test basic functionality
        result = ToolResult(output="Test successful")
        assert result.output == "Test successful"
        print("✓ ToolResult import and basic functionality test passed")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_presentation_agent_import_fix():
    """Test that presentation_agent.py has the correct import"""
    try:
        with open("app/agent/presentation_agent.py", "r") as f:
            content = f.read()
        
        # Check that the correct import is present
        if "from app.tool.base import ToolResult" in content:
            print("✓ Presentation agent has correct import")
        else:
            print("✗ Presentation agent missing correct import")
            return False
            
        # Check that the old import is not present
        if "from app.core.base_tool import ToolResult" in content:
            print("✗ Presentation agent still has old import")
            return False
        else:
            print("✓ Presentation agent old import removed")
            
        return True
    except Exception as e:
        print(f"✗ File check failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing import fix...")
    
    test1 = test_direct_import()
    test2 = test_presentation_agent_import_fix()
    
    if test1 and test2:
        print("\n✓ All tests passed! Import fix is successful.")
    else:
        print("\n✗ Some tests failed.")

