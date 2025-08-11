"""Shared test configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock, patch
from typing import Generator

from tests.mocks import MockOpenAIClient, MockAsyncOpenAIClient


@pytest.fixture
def mock_llm() -> Generator[Mock, None, None]:
    """Mock LLM for testing."""
    with patch('app.agent.base.LLM') as mock_llm_class:
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        yield mock_llm


@pytest.fixture
def mock_config() -> Generator[Mock, None, None]:
    """Mock config for testing."""
    with patch('app.config.config') as mock_config:
        yield mock_config


@pytest.fixture
def mock_sandbox_client() -> Generator[Mock, None, None]:
    """Mock sandbox client for testing."""
    with patch('app.sandbox.client.SANDBOX_CLIENT') as mock_client:
        mock_client.cleanup = Mock(return_value=None)
        yield mock_client


@pytest.fixture
def mock_logger() -> Generator[Mock, None, None]:
    """Mock logger for testing."""
    with patch('app.logger.logger') as mock_logger:
        yield mock_logger


# OpenAI API Mocking Fixtures

@pytest.fixture(autouse=True)
def mock_openai_api_key():
    """Automatically set a test OpenAI API key for all tests."""
    original_key = os.environ.get('OPENAI_API_KEY')
    os.environ['OPENAI_API_KEY'] = 'test-openai-key-for-testing'
    yield
    if original_key is not None:
        os.environ['OPENAI_API_KEY'] = original_key
    else:
        os.environ.pop('OPENAI_API_KEY', None)


@pytest.fixture(autouse=True)
def mock_openai_client():
    """Automatically mock OpenAI client for all tests."""
    with patch('openai.OpenAI', MockOpenAIClient) as mock_sync_client:
        with patch('openai.AsyncOpenAI', MockAsyncOpenAIClient) as mock_async_client:
            yield {
                'sync': mock_sync_client,
                'async': mock_async_client
            }


@pytest.fixture
def openai_mock_client() -> MockOpenAIClient:
    """Provide a mock OpenAI client instance for manual testing."""
    return MockOpenAIClient()


@pytest.fixture
def async_openai_mock_client() -> MockAsyncOpenAIClient:
    """Provide a mock async OpenAI client instance for manual testing."""
    return MockAsyncOpenAIClient()


@pytest.fixture
def reset_openai_mocks(mock_openai_client):
    """Reset all OpenAI mock states between tests."""
    yield
    # Reset is handled automatically by the autouse fixture