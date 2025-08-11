#!/usr/bin/env python3
"""Test script to verify Pydantic validation fix for Role enum."""

from app.schema import Message

def test_message_creation():
    """Test that Message creation with factory methods works without validation errors."""
    
    # Test user message
    user_msg = Message.user_message("Hello")
    assert user_msg.role == "user"
    assert user_msg.content == "Hello"
    print("✓ User message creation works")
    
    # Test system message
    system_msg = Message.system_message("System prompt")
    assert system_msg.role == "system"
    assert system_msg.content == "System prompt"
    print("✓ System message creation works")
    
    # Test assistant message
    assistant_msg = Message.assistant_message("I understand")
    assert assistant_msg.role == "assistant"
    assert assistant_msg.content == "I understand"
    print("✓ Assistant message creation works")
    
    # Test tool message
    tool_msg = Message.tool_message(
        content="Tool output",
        name="test_tool",
        tool_call_id="call_123"
    )
    assert tool_msg.role == "tool"
    assert tool_msg.content == "Tool output"
    assert tool_msg.name == "test_tool"
    assert tool_msg.tool_call_id == "call_123"
    print("✓ Tool message creation works")
    
    print("\n🎉 All message factory methods work correctly!")
    print("✅ Pydantic validation fix for Role enum is successful")

if __name__ == "__main__":
    test_message_creation()