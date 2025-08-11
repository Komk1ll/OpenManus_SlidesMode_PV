# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Spark_by_Manus** is a modernized AI agent system with multi-modal capabilities, featuring:
- **Agent Architecture**: BaseAgent with dependency injection support, specialized agents (Manus, Browser, Data Analysis, Presentation, etc.)
- **Tool System**: Modular tools for file operations, web browsing, Python execution, search, MCP integration, and presentation generation
- **Presentation System**: Complete presentation generation pipeline with multi-language support, image integration, and PDF export
- **Dependency Injection**: Modern DI architecture with interfaces, adapters, and factories for better testability
- **MCP Integration**: Model Context Protocol support for external tool integration
- **Multi-LLM Support**: OpenAI, Azure, Google, Ollama, and OpenRouter integrations

## Common Development Commands

### Testing
```bash
# Run all tests with coverage reporting
pytest --cov=app --cov-report=html:htmlcov --cov-report=term-missing --cov-report=xml

# Run presentation system tests (100% coverage)
python test_summary.py

# Run specific test categories
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m performance   # Performance tests
pytest -m di           # Dependency injection tests
```

### Development
```bash
# Run main Manus agent
python main.py --prompt "Your task here"

# Run presentation generation demo
python main_presentation.py

# Run with dependency injection
python run_di_demo.py

# Run MCP server
python run_mcp_server.py

# Run flow execution
python run_flow.py
```

### Configuration
- Main config: `config/config.toml`
- LLM models: Set in `[llm]` section with model, base_url, api_key
- MCP servers: Configure in `config/mcp.example.json`
- Environment variables: OPENAI_API_KEY, LOG_LEVEL, WORKSPACE_ROOT

## Architecture Overview

### Core Components

**Agent Layer** (`app/agent/`):
- `base.py` - BaseAgent with DI support, state management, memory, step-based execution
- `manus.py` - Main general-purpose agent with MCP support and browser context
- `presentation_agent.py` - Specialized agent for presentation generation
- `toolcall.py` - Tool calling agent base class
- `browser.py`, `swe.py`, `react.py` - Specialized agent types

**Tool Layer** (`app/tool/`):
- `base.py` - BaseTool interface with ToolResult
- `presentation_tools.py` - Complete presentation pipeline (structure, content, images, export)
- `browser_use_tool.py` - Browser automation using playwright
- `python_execute.py` - Safe Python code execution
- `search/` - Multiple search engines (Google, Bing, Baidu, DuckDuckGo)
- `mcp.py` - MCP client tools for external integration

**Infrastructure** (`app/`):
- `container.py` - Dependency injection container using dependency-injector
- `interfaces/` - Protocol definitions for LLM, logger, config, sandbox
- `adapters/` - Concrete implementations wrapping existing services
- `factories/` - Object creation with DI (AgentFactory, FlowFactory)

### Dependency Injection Pattern

The system supports both legacy direct instantiation and modern DI:

```python
# Legacy way (still works)
agent = Manus(name="test")

# DI way (recommended for new code)
container = Container.create_configured_container()
container.wire_modules()
agent_factory = container.agent_factory()
agent = agent_factory.create_agent("manus", "test")
```

### Agent Execution Flow

1. **Initialization**: Load config, initialize LLM, create tools
2. **Run Loop**: User input → Memory update → Think (LLM reasoning) → Tool calls → Results
3. **State Management**: IDLE → RUNNING → FINISHED with error handling
4. **Memory**: Persistent conversation history with role-based messages

## Key Files & Locations

### Configuration Files
- `config/config.toml` - Main configuration with LLM, browser, search, sandbox settings
- `pytest.ini` - Test configuration with coverage requirements (90% minimum)
- `requirements.txt` - Python dependencies with versions

### Critical Implementation Files
- `app/agent/base.py:18-275` - Core agent architecture
- `app/agent/manus.py:18-166` - Main agent implementation
- `app/container.py:14-130` - DI container setup
- `app/tool/presentation_tools.py` - Full presentation system

### Entry Points
- `main.py` - Basic Manus agent execution
- `main_presentation.py` - Presentation generation
- `run_di_demo.py` - Dependency injection example
- `run_mcp_server.py` - MCP server startup

## Presentation System Architecture

The presentation system is a complete pipeline with 4 main tools orchestrated by PresentationAgent:

1. **GenerateStructureTool** - Creates presentation outline with language detection
2. **GenerateSlideContentTool** - Generates rich content (paragraphs, bullets, code, quotes)
3. **SearchImageTool** - Finds images via Unsplash/Tavily with smart source selection
4. **ExportPresentationTool** - Exports to Markdown, HTML, JSON, PDF formats

**Language Support**: Auto-detects Russian (Cyrillic) vs English, generates culturally appropriate content

**API Integrations**: OpenAI/OpenRouter for content, Unsplash for professional images, Tavily for general images

## Testing Strategy

- **100% Coverage Target**: All components have comprehensive tests
- **Test Categories**: unit, integration, performance, di (dependency injection)
- **Presentation Tests**: 28 tests across 5 components (structure, content, image, export, agent)
- **Mocking**: Uses dependency injection for isolated unit testing

## Development Guidelines

### Agent Development
- Extend `BaseAgent` for new agent types
- Implement `step()` method for agent logic
- Use `update_memory()` for conversation management
- Support both legacy and DI initialization patterns

### Tool Development  
- Extend `BaseTool` with `execute()` method
- Return `ToolResult` with output/error/system fields
- Add to `ToolCollection` for agent usage
- Include comprehensive error handling

### Configuration
- Use TOML format for main config
- Support environment variable overrides
- Validate configuration in adapters
- Document all configuration options

### Best Practices
- Use dependency injection for new components
- Maintain backward compatibility with existing code
- Write comprehensive tests with mocks
- Follow the modular tool/agent architecture
- Use structured logging with correlation IDs