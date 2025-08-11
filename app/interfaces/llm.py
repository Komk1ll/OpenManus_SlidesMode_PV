"""LLM Provider Interface for dependency injection."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from app.schema import Message


class ILLMProvider(ABC):
    """Interface for Language Model providers.
    
    Provides abstraction over different LLM implementations (OpenAI, Anthropic, etc.)
    """

    @abstractmethod
    async def create_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a completion using the LLM.
        
        Args:
            messages: List of conversation messages
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Available tools for function calling
            tool_choice: Tool choice strategy
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Completion response from the LLM
        """
        pass

    @abstractmethod
    async def create_streaming_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs: Any,
    ):
        """Create a streaming completion using the LLM.
        
        Args:
            messages: List of conversation messages
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Available tools for function calling
            tool_choice: Tool choice strategy
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Streaming completion chunks from the LLM
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the current model name."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name (e.g., 'openai', 'anthropic')."""
        pass