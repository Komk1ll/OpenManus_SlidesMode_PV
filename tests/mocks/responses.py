"""Response generators for OpenAI API mocks.

Provides realistic response objects that match OpenAI API structure.
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from unittest.mock import Mock


class OpenAIResponseGenerator:
    """Generates realistic OpenAI API responses for testing."""
    
    @staticmethod
    def chat_completion(
        content: str = "This is a test response from the mocked OpenAI API.",
        model: str = "gpt-4",
        prompt_tokens: int = 10,
        completion_tokens: int = 15,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        finish_reason: str = "stop"
    ) -> Mock:
        """Generate a chat completion response.
        
        Args:
            content: Response content
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            tool_calls: Optional tool calls
            finish_reason: Reason for completion finish
            
        Returns:
            Mock object matching OpenAI ChatCompletion structure
        """
        response = Mock()
        response.id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
        response.object = "chat.completion"
        response.created = int(time.time())
        response.model = model
        response.system_fingerprint = None
        
        # Create choice
        choice = Mock()
        choice.index = 0
        choice.finish_reason = finish_reason
        
        # Create message
        message = Mock()
        message.role = "assistant"
        message.content = content
        message.tool_calls = tool_calls
        message.function_call = None
        
        choice.message = message
        response.choices = [choice]
        
        # Create usage
        usage = Mock()
        usage.prompt_tokens = prompt_tokens
        usage.completion_tokens = completion_tokens
        usage.total_tokens = prompt_tokens + completion_tokens
        
        response.usage = usage
        
        return response
    
    @staticmethod
    def chat_completion_stream(
        content: str = "This is a streaming response.",
        model: str = "gpt-4",
        chunk_size: int = 5
    ) -> List[Mock]:
        """Generate streaming chat completion responses.
        
        Args:
            content: Full response content to split into chunks
            model: Model name
            chunk_size: Size of each content chunk
            
        Returns:
            List of Mock objects representing stream chunks
        """
        chunks = []
        words = content.split()
        
        for i in range(0, len(words), chunk_size):
            chunk = Mock()
            chunk.id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
            chunk.object = "chat.completion.chunk"
            chunk.created = int(time.time())
            chunk.model = model
            
            choice = Mock()
            choice.index = 0
            choice.finish_reason = None
            
            delta = Mock()
            delta.role = "assistant" if i == 0 else None
            delta.content = " ".join(words[i:i+chunk_size]) + (" " if i + chunk_size < len(words) else "")
            
            choice.delta = delta
            chunk.choices = [choice]
            
            chunks.append(chunk)
        
        # Final chunk with finish_reason
        final_chunk = Mock()
        final_chunk.id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
        final_chunk.object = "chat.completion.chunk"
        final_chunk.created = int(time.time())
        final_chunk.model = model
        
        final_choice = Mock()
        final_choice.index = 0
        final_choice.finish_reason = "stop"
        final_choice.delta = Mock()
        final_choice.delta.content = None
        
        final_chunk.choices = [final_choice]
        chunks.append(final_chunk)
        
        return chunks
    
    @staticmethod
    def embedding(
        input_text: str = "test text",
        model: str = "text-embedding-ada-002",
        dimensions: int = 1536
    ) -> Mock:
        """Generate an embedding response.
        
        Args:
            input_text: Input text for embedding
            model: Embedding model name
            dimensions: Embedding vector dimensions
            
        Returns:
            Mock object matching OpenAI Embedding structure
        """
        response = Mock()
        response.object = "list"
        response.model = model
        
        # Create embedding data
        embedding_data = Mock()
        embedding_data.object = "embedding"
        embedding_data.index = 0
        # Generate fake embedding vector
        embedding_data.embedding = [0.1] * dimensions
        
        response.data = [embedding_data]
        
        # Create usage
        usage = Mock()
        usage.prompt_tokens = len(input_text.split())
        usage.total_tokens = usage.prompt_tokens
        
        response.usage = usage
        
        return response
    
    @staticmethod
    def file_object(
        filename: str = "test_file.txt",
        purpose: str = "fine-tune",
        file_size: int = 1024
    ) -> Mock:
        """Generate a file object response.
        
        Args:
            filename: Name of the file
            purpose: Purpose of the file
            file_size: Size of the file in bytes
            
        Returns:
            Mock object matching OpenAI File structure
        """
        file_obj = Mock()
        file_obj.id = f"file-{uuid.uuid4().hex[:24]}"
        file_obj.object = "file"
        file_obj.bytes = file_size
        file_obj.created_at = int(time.time())
        file_obj.filename = filename
        file_obj.purpose = purpose
        file_obj.status = "processed"
        file_obj.status_details = None
        
        return file_obj
    
    @staticmethod
    def error_response(
        error_type: str = "invalid_request_error",
        message: str = "Invalid request",
        code: Optional[str] = None
    ) -> Mock:
        """Generate an error response.
        
        Args:
            error_type: Type of error
            message: Error message
            code: Optional error code
            
        Returns:
            Mock object representing an OpenAI error
        """
        error = Mock()
        error.type = error_type
        error.message = message
        error.code = code
        
        response = Mock()
        response.error = error
        
        return response
    
    @staticmethod
    def tool_call_response(
        tool_name: str = "test_tool",
        tool_args: Dict[str, Any] = None,
        content: str = "Tool call executed successfully."
    ) -> Mock:
        """Generate a response with tool calls.
        
        Args:
            tool_name: Name of the tool being called
            tool_args: Arguments for the tool call
            content: Response content
            
        Returns:
            Mock object with tool calls
        """
        if tool_args is None:
            tool_args = {"param": "value"}
        
        tool_call = {
            "id": f"call_{uuid.uuid4().hex[:24]}",
            "type": "function",
            "function": {
                "name": tool_name,
                "arguments": str(tool_args)
            }
        }
        
        return OpenAIResponseGenerator.chat_completion(
            content=content,
            tool_calls=[tool_call],
            finish_reason="tool_calls"
        )