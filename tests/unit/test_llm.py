"""
Unit tests for app.llm module
Tests for OpenRouter integration, configuration errors, and token counting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tiktoken
from openai import APIError, AuthenticationError, RateLimitError

from app.llm import TokenCounter, LLMClient
from app.config import LLMSettings
from app.exceptions import TokenLimitExceeded


class TestTokenCounter:
    """Test cases for TokenCounter class"""

    @pytest.fixture
    def token_counter(self):
        """Create a TokenCounter instance with mocked tokenizer"""
        mock_tokenizer = Mock()
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        return TokenCounter(mock_tokenizer)

    def test_count_text_empty_string(self, token_counter):
        """Test token counting for empty string"""
        result = token_counter.count_text("")
        assert result == 0

    def test_count_text_normal_string(self, token_counter):
        """Test token counting for normal text"""
        result = token_counter.count_text("Hello world")
        assert result == 5  # Based on mock tokenizer

    def test_count_image_low_detail(self, token_counter):
        """Test token counting for low detail image"""
        image_item = {"detail": "low"}
        result = token_counter.count_image(image_item)
        assert result == TokenCounter.LOW_DETAIL_IMAGE_TOKENS

    def test_count_image_high_detail_with_dimensions(self, token_counter):
        """Test token counting for high detail image with dimensions"""
        image_item = {
            "detail": "high",
            "dimensions": (1024, 1024)
        }
        result = token_counter.count_image(image_item)
        # Expected calculation for 1024x1024 image
        expected = (4 * TokenCounter.HIGH_DETAIL_TILE_TOKENS) + TokenCounter.LOW_DETAIL_IMAGE_TOKENS
        assert result == expected

    def test_count_image_medium_detail_default(self, token_counter):
        """Test token counting for medium detail (default) image"""
        image_item = {"detail": "medium"}
        result = token_counter.count_image(image_item)
        # Should use high detail calculation with default dimensions
        assert result > TokenCounter.LOW_DETAIL_IMAGE_TOKENS

    def test_calculate_high_detail_tokens_large_image(self, token_counter):
        """Test high detail token calculation for large image that needs scaling"""
        # Image larger than MAX_SIZE
        result = token_counter._calculate_high_detail_tokens(4096, 2048)
        assert result > 0
        assert isinstance(result, int)

    def test_count_content_string(self, token_counter):
        """Test content token counting for string content"""
        result = token_counter.count_content("Hello world")
        assert result == 5

    def test_count_content_list_mixed(self, token_counter):
        """Test content token counting for mixed list content"""
        content = [
            "Hello",
            {"text": "world"},
            {"image_url": {"detail": "low"}}
        ]
        result = token_counter.count_content(content)
        expected = 5 + 5 + TokenCounter.LOW_DETAIL_IMAGE_TOKENS  # text + text + image
        assert result == expected

    def test_count_tool_calls(self, token_counter):
        """Test token counting for tool calls"""
        tool_calls = [
            {
                "function": {
                    "name": "test_function",
                    "arguments": '{"param": "value"}'
                }
            }
        ]
        result = token_counter.count_tool_calls(tool_calls)
        assert result == 10  # 5 tokens for name + 5 for arguments

    def test_count_message_tokens_basic(self, token_counter):
        """Test basic message token counting"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        result = token_counter.count_message_tokens(messages)
        # FORMAT_TOKENS + 2 * (BASE_MESSAGE_TOKENS + content tokens)
        expected = TokenCounter.FORMAT_TOKENS + 2 * (TokenCounter.BASE_MESSAGE_TOKENS + 5)
        assert result == expected


class TestLLMClient:
    """Test cases for LLMClient class"""

    @pytest.fixture
    def mock_settings(self):
        """Create mock LLM settings"""
        settings = Mock(spec=LLMSettings)
        settings.model = "test-model"
        settings.base_url = "https://api.test.com"
        settings.api_key = "test-key"
        settings.max_tokens = 1000
        settings.temperature = 0.7
        settings.api_type = "openai"
        return settings

    @pytest.fixture
    def llm_client(self, mock_settings):
        """Create LLMClient instance with mocked settings"""
        with patch('app.llm.config.llm', mock_settings):
            return LLMClient()

    def test_init_with_valid_config(self, mock_settings):
        """Test LLMClient initialization with valid configuration"""
        with patch('app.llm.config.llm', mock_settings):
            client = LLMClient()
            assert client.settings == mock_settings

    def test_init_with_missing_api_key(self):
        """Test LLMClient initialization with missing API key"""
        mock_settings = Mock(spec=LLMSettings)
        mock_settings.api_key = None
        
        with patch('app.llm.config.llm', mock_settings):
            with pytest.raises(ValueError, match="API key is required"):
                LLMClient()

    def test_init_with_invalid_model(self):
        """Test LLMClient initialization with invalid model"""
        mock_settings = Mock(spec=LLMSettings)
        mock_settings.model = ""
        mock_settings.api_key = "test-key"
        
        with patch('app.llm.config.llm', mock_settings):
            with pytest.raises(ValueError, match="Model name is required"):
                LLMClient()

    @patch('app.llm.AsyncOpenAI')
    def test_create_openai_client(self, mock_openai, llm_client):
        """Test OpenAI client creation"""
        client = llm_client._create_client()
        mock_openai.assert_called_once()

    @patch('app.llm.tiktoken.encoding_for_model')
    def test_get_tokenizer_success(self, mock_tiktoken, llm_client):
        """Test successful tokenizer retrieval"""
        mock_encoding = Mock()
        mock_tiktoken.return_value = mock_encoding
        
        tokenizer = llm_client._get_tokenizer()
        assert tokenizer == mock_encoding

    @patch('app.llm.tiktoken.encoding_for_model')
    def test_get_tokenizer_fallback(self, mock_tiktoken, llm_client):
        """Test tokenizer fallback to cl100k_base"""
        mock_tiktoken.side_effect = [KeyError("Model not found"), Mock()]
        
        tokenizer = llm_client._get_tokenizer()
        assert mock_tiktoken.call_count == 2

    @pytest.mark.asyncio
    async def test_chat_completion_success(self, llm_client):
        """Test successful chat completion"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        
        with patch.object(llm_client.client.chat.completions, 'create', return_value=mock_response):
            messages = [{"role": "user", "content": "Hello"}]
            response = await llm_client.chat_completion(messages)
            assert response == mock_response

    @pytest.mark.asyncio
    async def test_chat_completion_authentication_error(self, llm_client):
        """Test chat completion with authentication error"""
        with patch.object(llm_client.client.chat.completions, 'create', 
                         side_effect=AuthenticationError("Invalid API key", response=Mock(), body={})):
            messages = [{"role": "user", "content": "Hello"}]
            with pytest.raises(AuthenticationError):
                await llm_client.chat_completion(messages)

    @pytest.mark.asyncio
    async def test_chat_completion_rate_limit_error(self, llm_client):
        """Test chat completion with rate limit error"""
        with patch.object(llm_client.client.chat.completions, 'create', 
                         side_effect=RateLimitError("Rate limit exceeded", response=Mock(), body={})):
            messages = [{"role": "user", "content": "Hello"}]
            with pytest.raises(RateLimitError):
                await llm_client.chat_completion(messages)

    @pytest.mark.asyncio
    async def test_chat_completion_token_limit_exceeded(self, llm_client):
        """Test chat completion with token limit exceeded"""
        # Mock token counter to return high token count
        with patch.object(llm_client.token_counter, 'count_message_tokens', return_value=2000):
            llm_client.settings.max_tokens = 1000
            messages = [{"role": "user", "content": "Very long message"}]
            
            with pytest.raises(TokenLimitExceeded):
                await llm_client.chat_completion(messages)

    def test_count_tokens(self, llm_client):
        """Test token counting functionality"""
        messages = [{"role": "user", "content": "Hello"}]
        
        with patch.object(llm_client.token_counter, 'count_message_tokens', return_value=10):
            result = llm_client.count_tokens(messages)
            assert result == 10

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, llm_client):
        """Test retry mechanism for transient errors"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Success after retry"
        
        # First call fails, second succeeds
        with patch.object(llm_client.client.chat.completions, 'create', 
                         side_effect=[RateLimitError("Rate limit", response=Mock(), body={}), mock_response]):
            messages = [{"role": "user", "content": "Hello"}]
            
            # Should succeed after retry
            response = await llm_client.chat_completion(messages)
            assert response == mock_response


class TestLLMIntegration:
    """Integration tests for LLM functionality"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_openrouter_integration(self):
        """Test actual OpenRouter API integration (requires API key)"""
        # This test should only run when OPENROUTER_API_KEY is available
        import os
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not available")
        
        # Create real client with environment variables
        settings = LLMSettings(
            model="openai/gpt-3.5-turbo",
            base_url="https://openrouter.ai/api/v1/",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            max_tokens=100,
            temperature=0.7,
            api_type="openai"
        )
        
        with patch('app.llm.config.llm', settings):
            client = LLMClient()
            messages = [{"role": "user", "content": "Say hello in one word"}]
            
            response = await client.chat_completion(messages)
            assert response is not None
            assert hasattr(response, 'choices')
            assert len(response.choices) > 0


if __name__ == "__main__":
    pytest.main([__file__])

