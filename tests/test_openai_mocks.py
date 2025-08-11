"""Tests for OpenAI mock system.

Demonstrates how to use the centralized OpenAI mocking system.
"""

import pytest
import asyncio
from unittest.mock import patch

from tests.mocks import MockOpenAIClient, MockAsyncOpenAIClient, OpenAIResponseGenerator


class TestOpenAIMockSystem:
    """Test the OpenAI mock system functionality."""
    
    def test_mock_client_initialization(self, openai_mock_client):
        """Test that mock client initializes correctly."""
        assert openai_mock_client.api_key == "test-key"
        assert hasattr(openai_mock_client, 'chat')
        assert hasattr(openai_mock_client, 'embeddings')
        assert hasattr(openai_mock_client, 'files')
    
    def test_chat_completion_mock(self, openai_mock_client):
        """Test chat completion mocking."""
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        response = openai_mock_client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        assert response.model == "gpt-4"
        assert response.choices[0].message.role == "assistant"
        assert response.choices[0].message.content
        assert response.usage.total_tokens > 0
        assert openai_mock_client.chat.completions.call_count == 1
    
    def test_streaming_chat_completion(self, openai_mock_client):
        """Test streaming chat completion."""
        messages = [
            {"role": "user", "content": "Tell me a story"}
        ]
        
        stream = openai_mock_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=True
        )
        
        chunks = list(stream)
        assert len(chunks) > 1
        assert chunks[-1].choices[0].finish_reason == "stop"
        assert openai_mock_client.chat.completions.call_count == 1
    
    def test_embedding_mock(self, openai_mock_client):
        """Test embedding mocking."""
        response = openai_mock_client.embeddings.create(
            input="This is a test text",
            model="text-embedding-ada-002"
        )
        
        assert response.model == "text-embedding-ada-002"
        assert len(response.data) == 1
        assert len(response.data[0].embedding) == 1536
        assert response.usage.prompt_tokens > 0
        assert openai_mock_client.embeddings.call_count == 1
    
    def test_multiple_embeddings(self, openai_mock_client):
        """Test multiple text embeddings."""
        texts = ["First text", "Second text", "Third text"]
        
        response = openai_mock_client.embeddings.create(
            input=texts,
            model="text-embedding-ada-002"
        )
        
        assert len(response.data) == 3
        for i, embedding_data in enumerate(response.data):
            assert embedding_data.index == i
            assert len(embedding_data.embedding) == 1536
    
    def test_file_operations(self, openai_mock_client):
        """Test file operations mocking."""
        # Mock file object
        from io import StringIO
        mock_file = StringIO("test content")
        mock_file.name = "test.txt"
        
        # Create file
        file_response = openai_mock_client.files.create(
            file=mock_file,
            purpose="fine-tune"
        )
        
        assert file_response.filename == "test.txt"
        assert file_response.purpose == "fine-tune"
        assert file_response.id.startswith("file-")
        
        # List files
        list_response = openai_mock_client.files.list()
        assert len(list_response.data) == 1
        assert list_response.data[0].id == file_response.id
        
        # Delete file
        delete_response = openai_mock_client.files.delete(file_response.id)
        assert delete_response.deleted is True
        assert delete_response.id == file_response.id
    
    def test_custom_response_setting(self, openai_mock_client):
        """Test setting custom responses."""
        custom_response = OpenAIResponseGenerator.chat_completion(
            content="This is a custom response",
            model="gpt-3.5-turbo"
        )
        
        openai_mock_client.chat.completions.set_custom_response(
            custom_response,
            model="gpt-3.5-turbo"
        )
        
        response = openai_mock_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        assert response.choices[0].message.content == "This is a custom response"
        assert response.model == "gpt-3.5-turbo"
    
    def test_mock_reset(self, openai_mock_client):
        """Test resetting mock states."""
        # Make some calls
        openai_mock_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test"}]
        )
        openai_mock_client.embeddings.create(
            input="Test text",
            model="text-embedding-ada-002"
        )
        
        assert openai_mock_client.chat.completions.call_count == 1
        assert openai_mock_client.embeddings.call_count == 1
        
        # Reset all mocks
        openai_mock_client.reset_all_mocks()
        
        assert openai_mock_client.chat.completions.call_count == 0
        assert openai_mock_client.embeddings.call_count == 0


class TestAsyncOpenAIMocks:
    """Test async OpenAI mock functionality."""
    
    @pytest.mark.asyncio
    async def test_async_chat_completion(self, async_openai_mock_client):
        """Test async chat completion."""
        messages = [
            {"role": "user", "content": "Hello async world!"}
        ]
        
        response = await async_openai_mock_client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        assert response.model == "gpt-4"
        assert response.choices[0].message.role == "assistant"
        assert response.choices[0].message.content
        assert async_openai_mock_client.chat.completions.call_count == 1
    
    @pytest.mark.asyncio
    async def test_async_streaming_chat(self, async_openai_mock_client):
        """Test async streaming chat completion."""
        messages = [
            {"role": "user", "content": "Stream me a response"}
        ]
        
        stream = await async_openai_mock_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=True
        )
        
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        
        assert len(chunks) > 1
        assert chunks[-1].choices[0].finish_reason == "stop"
    
    @pytest.mark.asyncio
    async def test_async_embeddings(self, async_openai_mock_client):
        """Test async embeddings."""
        response = await async_openai_mock_client.embeddings.create(
            input="Async embedding test",
            model="text-embedding-ada-002"
        )
        
        assert response.model == "text-embedding-ada-002"
        assert len(response.data) == 1
        assert len(response.data[0].embedding) == 1536
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async client as context manager."""
        async with MockAsyncOpenAIClient() as client:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Test context manager"}]
            )
            assert response.model == "gpt-4"


class TestResponseGenerator:
    """Test the response generator utility."""
    
    def test_chat_completion_generation(self):
        """Test chat completion response generation."""
        response = OpenAIResponseGenerator.chat_completion(
            content="Test response",
            model="gpt-4",
            prompt_tokens=10,
            completion_tokens=5
        )
        
        assert response.model == "gpt-4"
        assert response.choices[0].message.content == "Test response"
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 5
        assert response.usage.total_tokens == 15
    
    def test_tool_call_generation(self):
        """Test tool call response generation."""
        response = OpenAIResponseGenerator.tool_call_response(
            tool_name="search_function",
            tool_args={"query": "test"},
            content="I'll search for that."
        )
        
        assert response.choices[0].message.tool_calls is not None
        assert len(response.choices[0].message.tool_calls) == 1
        assert response.choices[0].message.tool_calls[0]["function"]["name"] == "search_function"
        assert response.choices[0].finish_reason == "tool_calls"
    
    def test_error_response_generation(self):
        """Test error response generation."""
        error_response = OpenAIResponseGenerator.error_response(
            error_type="rate_limit_exceeded",
            message="Too many requests",
            code="rate_limit"
        )
        
        assert error_response.error.type == "rate_limit_exceeded"
        assert error_response.error.message == "Too many requests"
        assert error_response.error.code == "rate_limit"


class TestIntegrationWithExistingCode:
    """Test integration with existing codebase."""
    
    def test_automatic_mocking_works(self):
        """Test that automatic mocking is working."""
        # This test verifies that the autouse fixtures are working
        # by importing and using OpenAI directly
        import openai
        
        client = openai.OpenAI(api_key="test-key")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test automatic mocking"}]
        )
        
        # Should get a mock response, not a real API call
        assert response.model == "gpt-4"
        assert response.choices[0].message.content
    
    @pytest.mark.asyncio
    async def test_automatic_async_mocking(self):
        """Test that automatic async mocking works."""
        import openai
        
        async_client = openai.AsyncOpenAI(api_key="test-key")
        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test async automatic mocking"}]
        )
        
        assert response.model == "gpt-4"
        assert response.choices[0].message.content
    
    def test_environment_variable_mocking(self):
        """Test that OPENAI_API_KEY is automatically set."""
        import os
        
        # The autouse fixture should have set this
        assert os.environ.get('OPENAI_API_KEY') == 'test-openai-key-for-testing'