"""OpenAI-specific test fixtures and utilities.

Provides specialized fixtures for testing OpenAI API interactions.
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock

from tests.mocks import OpenAIResponseGenerator


@pytest.fixture
def openai_chat_response():
    """Standard chat completion response."""
    return OpenAIResponseGenerator.chat_completion(
        content="Hello! This is a test response from the AI assistant.",
        model="gpt-4",
        prompt_tokens=20,
        completion_tokens=12
    )


@pytest.fixture
def openai_streaming_response():
    """Streaming chat completion response."""
    return OpenAIResponseGenerator.chat_completion_stream(
        content="This is a streaming response from the AI.",
        model="gpt-4",
        chunk_size=3
    )


@pytest.fixture
def openai_tool_call_response():
    """Chat completion with tool calls."""
    return OpenAIResponseGenerator.tool_call_response(
        tool_name="search_web",
        tool_args={"query": "test search", "limit": 5},
        content="I'll search for that information."
    )


@pytest.fixture
def openai_embedding_response():
    """Standard embedding response."""
    return OpenAIResponseGenerator.embedding(
        input_text="This is test text for embedding",
        model="text-embedding-ada-002",
        dimensions=1536
    )


@pytest.fixture
def openai_file_response():
    """File upload response."""
    return OpenAIResponseGenerator.file_object(
        filename="test_data.jsonl",
        purpose="fine-tune",
        file_size=2048
    )


@pytest.fixture
def openai_error_response():
    """Error response for testing error handling."""
    return OpenAIResponseGenerator.error_response(
        error_type="rate_limit_exceeded",
        message="Rate limit exceeded. Please try again later.",
        code="rate_limit_exceeded"
    )


@pytest.fixture
def custom_openai_responses():
    """Factory for creating custom OpenAI responses."""
    def _create_response(
        response_type: str,
        **kwargs
    ) -> Mock:
        """Create custom OpenAI response.
        
        Args:
            response_type: Type of response ('chat', 'embedding', 'file', 'error')
            **kwargs: Additional parameters for response generation
            
        Returns:
            Mock response object
        """
        if response_type == "chat":
            return OpenAIResponseGenerator.chat_completion(**kwargs)
        elif response_type == "chat_stream":
            return OpenAIResponseGenerator.chat_completion_stream(**kwargs)
        elif response_type == "embedding":
            return OpenAIResponseGenerator.embedding(**kwargs)
        elif response_type == "file":
            return OpenAIResponseGenerator.file_object(**kwargs)
        elif response_type == "error":
            return OpenAIResponseGenerator.error_response(**kwargs)
        elif response_type == "tool_call":
            return OpenAIResponseGenerator.tool_call_response(**kwargs)
        else:
            raise ValueError(f"Unknown response type: {response_type}")
    
    return _create_response


@pytest.fixture
def openai_conversation_history():
    """Sample conversation history for testing."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you! How can I help you today?"},
        {"role": "user", "content": "Can you help me with a coding problem?"}
    ]


@pytest.fixture
def openai_test_scenarios():
    """Common test scenarios for OpenAI API testing."""
    return {
        "simple_chat": {
            "messages": [
                {"role": "user", "content": "Say hello"}
            ],
            "expected_response": "Hello! How can I help you today?"
        },
        "code_generation": {
            "messages": [
                {"role": "user", "content": "Write a Python function to calculate factorial"}
            ],
            "expected_response": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)"
        },
        "tool_usage": {
            "messages": [
                {"role": "user", "content": "Search for information about Python testing"}
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_web",
                        "description": "Search the web for information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "limit": {"type": "integer"}
                            }
                        }
                    }
                }
            ]
        },
        "embedding_test": {
            "input": "This is a test document for embedding",
            "model": "text-embedding-ada-002"
        }
    }


@pytest.fixture
def mock_openai_with_custom_responses(openai_mock_client, custom_openai_responses):
    """OpenAI mock client with ability to set custom responses."""
    def _set_response(endpoint: str, **kwargs):
        """Set custom response for specific endpoint.
        
        Args:
            endpoint: API endpoint ('chat', 'embedding', etc.)
            **kwargs: Response parameters
        """
        if endpoint == "chat":
            response = custom_openai_responses("chat", **kwargs)
            openai_mock_client.chat.completions.set_custom_response(response)
        elif endpoint == "embedding":
            response = custom_openai_responses("embedding", **kwargs)
            # Note: Embeddings don't have set_custom_response in our current implementation
            # This would need to be added if needed
        # Add more endpoints as needed
    
    openai_mock_client.set_custom_response = _set_response
    return openai_mock_client