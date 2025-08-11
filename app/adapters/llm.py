"""OpenAI LLM Provider Adapter implementing ILLMProvider interface."""

from typing import Any, Dict, List, Optional, Union

from app.interfaces.llm import ILLMProvider
from app.llm import LLM as LegacyLLM
from app.schema import Message


class OpenAIProvider(ILLMProvider):
    """OpenAI LLM provider adapter wrapping the legacy LLM class.
    
    Provides a clean interface to the existing LLM system while
    maintaining backward compatibility.
    """

    def __init__(self, config_name: str = "default", llm_config: Optional[Dict[str, Any]] = None):
        """Initialize the OpenAI provider.
        
        Args:
            config_name: Name of the LLM configuration to use
            llm_config: Optional LLM configuration override
        """
        self._config_name = config_name
        self._llm_config = llm_config
        self._llm = None

    @property
    def _client(self) -> LegacyLLM:
        """Lazy initialization of the LLM client."""
        if self._llm is None:
            self._llm = LegacyLLM(self._config_name, self._llm_config)
        return self._llm

    async def create_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> str:
        """Create a completion using the LLM.
        
        Args:
            messages: List of conversation messages
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            tools: Optional tools for function calling
            tool_choice: Optional tool choice specification
            **kwargs: Additional arguments
            
        Returns:
            The generated completion text
        """
        # Convert Message objects to legacy format if needed
        legacy_messages = []
        for msg in messages:
            if isinstance(msg, Message):
                legacy_messages.append(msg.to_dict())
            else:
                legacy_messages.append(msg)
        
        # Use legacy LLM's ask method for non-streaming completion
        # Note: The legacy LLM doesn't directly support tools in ask method,
        # so we'll need to use the completion method for tool calls
        if tools or tool_choice:
            return await self._create_completion_with_tools(
                legacy_messages, model, temperature, max_tokens, tools, tool_choice, **kwargs
            )
        
        # For simple completions, use the ask method
        response = await self._client.ask(
            messages=legacy_messages,
            stream=False,
            temperature=temperature or self._client.temperature,
        )
        
        return response

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
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            tools: Optional tools for function calling
            tool_choice: Optional tool choice specification
            **kwargs: Additional arguments
            
        Yields:
            Streaming completion chunks
        """
        # Convert Message objects to legacy format if needed
        legacy_messages = []
        for msg in messages:
            if isinstance(msg, Message):
                legacy_messages.append(msg.to_dict())
            else:
                legacy_messages.append(msg)
        
        # For streaming, we'll need to use the legacy LLM's streaming capabilities
        # This is a simplified implementation - the legacy LLM's streaming
        # interface may need to be adapted
        if tools or tool_choice:
            async for chunk in self._create_streaming_completion_with_tools(
                legacy_messages, model, temperature, max_tokens, tools, tool_choice, **kwargs
            ):
                yield chunk
        else:
            # Use the ask method with streaming enabled
            response = await self._client.ask(
                messages=legacy_messages,
                stream=True,
                temperature=temperature or self._client.temperature,
            )
            # Note: The legacy ask method returns a string, not a stream
            # This would need to be adapted based on the actual streaming implementation
            yield response

    async def _create_completion_with_tools(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        tools: Optional[List[Dict[str, Any]]],
        tool_choice: Optional[Union[str, Dict[str, Any]]],
        **kwargs: Any,
    ) -> str:
        """Create completion with tools using legacy LLM's completion method."""
        # This would need to be implemented based on the legacy LLM's
        # tool calling capabilities. For now, we'll use a basic implementation.
        
        # Prepare completion parameters
        completion_kwargs = {
            "model": model or self._client.model,
            "temperature": temperature or self._client.temperature,
            "max_tokens": max_tokens or self._client.max_tokens,
        }
        
        if tools:
            completion_kwargs["tools"] = tools
        if tool_choice:
            completion_kwargs["tool_choice"] = tool_choice
        
        completion_kwargs.update(kwargs)
        
        # Use the legacy LLM's completion method
        # Note: This assumes the legacy LLM has a completion method that supports tools
        if hasattr(self._client, 'completion'):
            response = await self._client.completion(messages=messages, **completion_kwargs)
            # Extract text from response based on the legacy LLM's response format
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].message.content or ""
            return str(response)
        else:
            # Fallback to ask method without tools
            return await self._client.ask(
                messages=messages,
                stream=False,
                temperature=temperature or self._client.temperature,
            )

    async def _create_streaming_completion_with_tools(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        tools: Optional[List[Dict[str, Any]]],
        tool_choice: Optional[Union[str, Dict[str, Any]]],
        **kwargs: Any,
    ):
        """Create streaming completion with tools."""
        # This is a placeholder implementation
        # The actual implementation would depend on the legacy LLM's streaming capabilities
        response = await self._create_completion_with_tools(
            messages, model, temperature, max_tokens, tools, tool_choice, **kwargs
        )
        yield response

    @property
    def model_name(self) -> str:
        """Get the current model name."""
        return self._client.model

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return f"openai-{self._client.api_type}"

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the LLM's tokenizer."""
        return self._client.count_tokens(text)

    def get_token_usage(self) -> Dict[str, int]:
        """Get current token usage statistics."""
        return {
            "total_input_tokens": self._client.total_input_tokens,
            "total_completion_tokens": self._client.total_completion_tokens,
            "total_tokens": self._client.total_input_tokens + self._client.total_completion_tokens,
        }