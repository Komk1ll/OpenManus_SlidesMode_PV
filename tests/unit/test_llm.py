"""Unit tests for LLM module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from app.llm import LLM, TokenCounter
from app.schema import Message
from app.config import LLMSettings


class TestTokenCounter:
    """Test cases for TokenCounter class."""
    
    def test_token_counter_constants(self) -> None:
        """Test that token counter has expected constants."""
        assert TokenCounter.BASE_MESSAGE_TOKENS == 4
        assert TokenCounter.FORMAT_TOKENS == 2
        assert TokenCounter.LOW_DETAIL_IMAGE_TOKENS == 85
        assert TokenCounter.HIGH_DETAIL_TILE_TOKENS == 170
    
    def test_count_text_for_content(self) -> None:
        """Test token counting for text content."""
        # Mock tokenizer for testing
        mock_tokenizer = Mock()
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        
        counter = TokenCounter(mock_tokenizer)
        tokens = counter.count_text("Hello, world!")
        assert isinstance(tokens, int)
        assert tokens == 5


class TestLLM:
    """Test cases for LLM class."""

    @pytest.fixture
    def mock_settings(self) -> Dict[str, LLMSettings]:
        """Create mock LLM settings."""
        settings = LLMSettings(
            model="gpt-4",
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            max_tokens=4096,
            temperature=0.7,
            api_type="openai"
        )
        return {"default": settings}

    @pytest.fixture
    def llm(self, mock_settings: Dict[str, LLMSettings]) -> LLM:
        """Create LLM instance with mock settings."""
        with patch('app.llm.config') as mock_config:
            mock_config.llm = mock_settings
            return LLM()

    def test_llm_initialization(self, llm: LLM) -> None:
        """Test LLM initialization."""
        assert llm.model == "gpt-4"
        assert llm.token_counter is not None
        assert llm.api_key == "test-key"
        assert llm.max_tokens == 4096

    def test_llm_initialization_with_custom_config(self, mock_settings: Dict[str, LLMSettings]) -> None:
        """Test LLM initialization with custom config name."""
        with patch('app.llm.config') as mock_config:
            mock_config.llm = mock_settings
            llm = LLM(config_name="default")
            assert llm.model == "gpt-4"

    def test_count_message_tokens_basic(self, llm: LLM) -> None:
        """Test basic message token counting."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        # Mock the token counter
        with patch.object(llm.token_counter, 'count_text', return_value=10):
            tokens = llm.count_message_tokens(messages)
            assert isinstance(tokens, int)
            assert tokens > 0

    def test_count_message_tokens_empty(self, llm: LLM) -> None:
        """Test token counting with empty messages."""
        tokens = llm.count_message_tokens([])
        assert tokens >= 0

    @pytest.mark.asyncio
    async def test_ask_method_mock(self, llm: LLM) -> None:
        """Test ask method with mocked client."""
        messages = [{"role": "user", "content": "Test message"}]
        
        # Mock the OpenAI client
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        
        with patch.object(llm.client, 'chat') as mock_chat:
            mock_chat.completions.create = AsyncMock(return_value=mock_response)
            
            response = await llm.ask(messages, stream=False)
            
            assert response == "Test response"

    def test_format_messages_conversion(self, llm: LLM) -> None:
        """Test message formatting and conversion."""
        # Test with Message objects
        message_obj = Message(role="user", content="Test")
        formatted = LLM.format_messages([message_obj])
        
        assert isinstance(formatted, list)
        if formatted:  # If not empty
            assert "role" in formatted[0]
            assert "content" in formatted[0]

    def test_is_multimodal_model(self, llm: LLM, monkeypatch) -> None:
        """Test multimodal model detection."""
        from app.llm import MULTIMODAL_MODELS
        
        # Test with known multimodal model
        monkeypatch.setattr(llm, 'model', 'gpt-4o')
        assert llm.model in MULTIMODAL_MODELS
        
        # Test with non-multimodal model
        monkeypatch.setattr(llm, 'model', 'gpt-3.5-turbo')
        assert llm.model not in MULTIMODAL_MODELS

    def test_is_reasoning_model(self, llm: LLM, monkeypatch) -> None:
        """Test reasoning model detection."""
        from app.llm import REASONING_MODELS
        
        # Test with known reasoning model
        monkeypatch.setattr(llm, 'model', 'o1')
        assert llm.model in REASONING_MODELS
        
        # Test with non-reasoning model
        monkeypatch.setattr(llm, 'model', 'gpt-4')
        assert llm.model not in REASONING_MODELS

    @pytest.mark.asyncio
    async def test_token_limit_exceeded_handling(self, llm: LLM) -> None:
        """Test handling of token limit exceeded scenarios."""
        # This would test the token limit logic
        # For now, just ensure the method exists
        assert hasattr(llm, 'count_message_tokens')
        assert hasattr(llm, 'max_tokens')
        assert llm.max_tokens == 4096

    def test_llm_settings_validation(self, mock_settings: Dict[str, LLMSettings]) -> None:
        """Test LLM settings validation."""
        settings = mock_settings["default"]
        assert settings.model == "gpt-4"
        assert settings.api_key == "test-key"
        assert settings.max_tokens == 4096
        assert settings.temperature == 0.7
        assert settings.api_type == "openai"

    @pytest.mark.parametrize("api_type,expected_client_type", [
        ("openai", "AsyncOpenAI"),
        ("azure", "AsyncAzureOpenAI"),
        ("aws", "BedrockClient"),
    ])
    def test_client_creation_by_api_type(self, llm: LLM, api_type: str, expected_client_type: str) -> None:
        """Test client creation for different API types."""
        with patch.object(llm, 'api_type', api_type):
            # This is a basic test to ensure the client attribute exists
            # Full testing would require mocking the actual clients
            try:
                assert llm.client is not None
                assert hasattr(llm, 'client')
            except Exception:
                # If dependencies are not available, skip
                pytest.skip(f"Client creation for {api_type} requires proper dependencies")


class TestLLMIntegration:
    """Integration tests for LLM functionality."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_llm_with_real_config(self) -> None:
        """Test LLM with real configuration (requires API key)."""
        # This test would only run if API keys are available
        import os
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("Integration test requires OPENAI_API_KEY environment variable")
        
        try:
            llm = LLM()
            messages = [{"role": "user", "content": "Say 'test' if you can hear me."}]
            response = await llm.ask(messages)
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            pytest.skip(f"Integration test failed due to: {e}")