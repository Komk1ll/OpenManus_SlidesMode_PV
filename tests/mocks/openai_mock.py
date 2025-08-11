"""Mock OpenAI client for testing.

Provides drop-in replacement for OpenAI client with configurable responses.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, AsyncIterator, Iterator
from unittest.mock import Mock, AsyncMock

from .responses import OpenAIResponseGenerator


class MockChatCompletions:
    """Mock for OpenAI chat completions."""
    
    def __init__(self, response_generator: OpenAIResponseGenerator):
        self.response_generator = response_generator
        self._custom_responses = {}
        self._call_count = 0
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        **kwargs
    ) -> Union[Mock, Iterator[Mock]]:
        """Create a chat completion.
        
        Args:
            model: Model name
            messages: List of messages
            stream: Whether to stream response
            **kwargs: Additional parameters
            
        Returns:
            Mock response or iterator of mock chunks
        """
        self._call_count += 1
        
        # Check for custom response
        key = self._get_response_key(model, messages, stream)
        if key in self._custom_responses:
            return self._custom_responses[key]
        
        # Generate default response
        if stream:
            return iter(self.response_generator.chat_completion_stream(
                model=model
            ))
        else:
            return self.response_generator.chat_completion(
                model=model
            )
    
    def set_custom_response(
        self,
        response: Any,
        model: str = None,
        messages: List[Dict[str, Any]] = None,
        stream: bool = False
    ):
        """Set a custom response for specific parameters.
        
        Args:
            response: Custom response to return
            model: Model name to match (None for any)
            messages: Messages to match (None for any)
            stream: Stream flag to match
        """
        key = self._get_response_key(model, messages, stream)
        self._custom_responses[key] = response
    
    def _get_response_key(self, model, messages, stream):
        """Generate key for response mapping."""
        # Use model as primary key, ignore messages for simplicity
        return (
            model or "*",
            stream
        )
    
    @property
    def call_count(self) -> int:
        """Number of times create was called."""
        return self._call_count
    
    def reset(self):
        """Reset call count and custom responses."""
        self._call_count = 0
        self._custom_responses.clear()


class MockAsyncChatCompletions:
    """Async mock for OpenAI chat completions."""
    
    def __init__(self, response_generator: OpenAIResponseGenerator):
        self.response_generator = response_generator
        self._custom_responses = {}
        self._call_count = 0
    
    async def create(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        **kwargs
    ) -> Union[Mock, AsyncIterator[Mock]]:
        """Create a chat completion asynchronously.
        
        Args:
            model: Model name
            messages: List of messages
            stream: Whether to stream response
            **kwargs: Additional parameters
            
        Returns:
            Mock response or async iterator of mock chunks
        """
        self._call_count += 1
        
        # Check for custom response
        key = self._get_response_key(model, messages, stream)
        if key in self._custom_responses:
            response = self._custom_responses[key]
            if stream and hasattr(response, '__aiter__'):
                return response
            elif not stream:
                return response
        
        # Generate default response
        if stream:
            return self._async_stream_generator(model)
        else:
            # Simulate async delay
            await asyncio.sleep(0.01)
            return self.response_generator.chat_completion(
                model=model
            )
    
    async def _async_stream_generator(self, model: str) -> AsyncIterator[Mock]:
        """Generate async stream of mock chunks."""
        chunks = self.response_generator.chat_completion_stream(model=model)
        for chunk in chunks:
            await asyncio.sleep(0.001)  # Simulate streaming delay
            yield chunk
    
    def set_custom_response(
        self,
        response: Any,
        model: str = None,
        messages: List[Dict[str, Any]] = None,
        stream: bool = False
    ):
        """Set a custom response for specific parameters."""
        key = self._get_response_key(model, messages, stream)
        self._custom_responses[key] = response
    
    def _get_response_key(self, model, messages, stream):
        """Generate key for response mapping."""
        # Use model as primary key, ignore messages for simplicity
        return (
            model or "*",
            stream
        )
    
    @property
    def call_count(self) -> int:
        """Number of times create was called."""
        return self._call_count
    
    def reset(self):
        """Reset call count and custom responses."""
        self._call_count = 0
        self._custom_responses.clear()


class MockEmbeddings:
    """Mock for OpenAI embeddings."""
    
    def __init__(self, response_generator: OpenAIResponseGenerator):
        self.response_generator = response_generator
        self._call_count = 0
    
    def create(
        self,
        input: Union[str, List[str]],
        model: str = "text-embedding-ada-002",
        **kwargs
    ) -> Mock:
        """Create embeddings.
        
        Args:
            input: Text input(s) to embed
            model: Embedding model name
            **kwargs: Additional parameters
            
        Returns:
            Mock embedding response
        """
        self._call_count += 1
        
        if isinstance(input, list):
            # Multiple inputs
            response = Mock()
            response.object = "list"
            response.model = model
            response.data = []
            
            total_tokens = 0
            for i, text in enumerate(input):
                embedding_data = Mock()
                embedding_data.object = "embedding"
                embedding_data.index = i
                embedding_data.embedding = [0.1] * 1536  # Default dimensions
                response.data.append(embedding_data)
                total_tokens += len(text.split())
            
            usage = Mock()
            usage.prompt_tokens = total_tokens
            usage.total_tokens = total_tokens
            response.usage = usage
            
            return response
        else:
            return self.response_generator.embedding(
                input_text=input,
                model=model
            )
    
    @property
    def call_count(self) -> int:
        """Number of times create was called."""
        return self._call_count
    
    def reset(self):
        """Reset call count."""
        self._call_count = 0


class MockAsyncEmbeddings:
    """Async mock for OpenAI embeddings."""
    
    def __init__(self, response_generator: OpenAIResponseGenerator):
        self.response_generator = response_generator
        self._call_count = 0
    
    async def create(
        self,
        input: Union[str, List[str]],
        model: str = "text-embedding-ada-002",
        **kwargs
    ) -> Mock:
        """Create embeddings asynchronously."""
        self._call_count += 1
        
        # Simulate async delay
        await asyncio.sleep(0.01)
        
        if isinstance(input, list):
            # Multiple inputs
            response = Mock()
            response.object = "list"
            response.model = model
            response.data = []
            
            total_tokens = 0
            for i, text in enumerate(input):
                embedding_data = Mock()
                embedding_data.object = "embedding"
                embedding_data.index = i
                embedding_data.embedding = [0.1] * 1536
                response.data.append(embedding_data)
                total_tokens += len(text.split())
            
            usage = Mock()
            usage.prompt_tokens = total_tokens
            usage.total_tokens = total_tokens
            response.usage = usage
            
            return response
        else:
            return self.response_generator.embedding(
                input_text=input,
                model=model
            )
    
    @property
    def call_count(self) -> int:
        """Number of times create was called."""
        return self._call_count
    
    def reset(self):
        """Reset call count."""
        self._call_count = 0


class MockFiles:
    """Mock for OpenAI files API."""
    
    def __init__(self, response_generator: OpenAIResponseGenerator):
        self.response_generator = response_generator
        self._files = {}
        self._call_count = 0
    
    def create(self, file, purpose: str, **kwargs) -> Mock:
        """Create a file."""
        self._call_count += 1
        filename = getattr(file, 'name', 'uploaded_file.txt')
        file_obj = self.response_generator.file_object(
            filename=filename,
            purpose=purpose
        )
        self._files[file_obj.id] = file_obj
        return file_obj
    
    def list(self, purpose: str = None) -> Mock:
        """List files."""
        files = list(self._files.values())
        if purpose:
            files = [f for f in files if f.purpose == purpose]
        
        response = Mock()
        response.object = "list"
        response.data = files
        return response
    
    def delete(self, file_id: str) -> Mock:
        """Delete a file."""
        if file_id in self._files:
            del self._files[file_id]
        
        response = Mock()
        response.id = file_id
        response.object = "file"
        response.deleted = True
        return response
    
    @property
    def call_count(self) -> int:
        return self._call_count
    
    def reset(self):
        """Reset files and call count."""
        self._files.clear()
        self._call_count = 0


class MockOpenAIClient:
    """Mock OpenAI client for synchronous operations."""
    
    def __init__(self, api_key: str = "test-key", **kwargs):
        self.api_key = api_key
        self.response_generator = OpenAIResponseGenerator()
        
        # Initialize API endpoints
        self.chat = Mock()
        self.chat.completions = MockChatCompletions(self.response_generator)
        
        self.embeddings = MockEmbeddings(self.response_generator)
        self.files = MockFiles(self.response_generator)
    
    def reset_all_mocks(self):
        """Reset all mock states."""
        self.chat.completions.reset()
        self.embeddings.reset()
        self.files.reset()


class MockAsyncOpenAIClient:
    """Mock OpenAI client for asynchronous operations."""
    
    def __init__(self, api_key: str = "test-key", **kwargs):
        self.api_key = api_key
        self.response_generator = OpenAIResponseGenerator()
        
        # Initialize API endpoints
        self.chat = Mock()
        self.chat.completions = MockAsyncChatCompletions(self.response_generator)
        
        self.embeddings = MockAsyncEmbeddings(self.response_generator)
        # Note: Files API is typically not async in OpenAI client
        self.files = MockFiles(self.response_generator)
    
    def reset_all_mocks(self):
        """Reset all mock states."""
        self.chat.completions.reset()
        self.embeddings.reset()
        self.files.reset()
    
    async def close(self):
        """Close the client (no-op for mock)."""
        pass
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()