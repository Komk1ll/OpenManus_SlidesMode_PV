# Dependency Injection Architecture

This document describes the dependency injection (DI) architecture implemented in Spark, which provides better modularity, testability, and maintainability.

## Overview

The DI architecture introduces:
- **Interfaces**: Abstract contracts for core services
- **Adapters**: Concrete implementations of interfaces
- **Container**: Central dependency management
- **Factories**: Object creation with DI
- **Backward Compatibility**: Existing code continues to work

## Architecture Components

### 1. Interfaces (`app/interfaces/`)

Define contracts for core services:

```python
# app/interfaces/llm.py
class ILLMProvider(Protocol):
    async def generate_response(self, messages: List[Dict]) -> str: ...

# app/interfaces/logger.py  
class ILogger(Protocol):
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...

# app/interfaces/config.py
class IConfig(Protocol):
    workspace_root: str
    log_level: str

# app/interfaces/sandbox.py
class ISandboxClient(Protocol):
    async def create_sandbox(self) -> str: ...
    async def run_command(self, command: str) -> str: ...
```

### 2. Adapters (`app/adapters/`)

Concrete implementations that wrap existing services:

```python
# app/adapters/llm.py
class OpenAIProvider(ILLMProvider):
    def __init__(self, config: IConfig, logger: ILogger, ...):
        # Wraps existing LLM functionality

# app/adapters/logger.py
class StructuredLogger(ILogger):
    def __init__(self, level: str, correlation_id: str):
        # Wraps existing logger

# app/adapters/config.py
class AppConfig(IConfig):
    def __init__(self, workspace_root: str, log_level: str):
        # Wraps existing config

# app/adapters/sandbox.py
class SandboxClientAdapter(ISandboxClient):
    def __init__(self, logger: ILogger, config: IConfig):
        # Wraps existing SANDBOX_CLIENT
```

### 3. Container (`app/container.py`)

Central dependency management using `dependency-injector`:

```python
class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Core services
    logger = providers.Singleton("app.adapters.logger.StructuredLogger", ...)
    app_config = providers.Singleton("app.adapters.config.AppConfig", ...)
    llm_provider = providers.Factory("app.adapters.llm.OpenAIProvider", ...)
    sandbox_client = providers.Singleton("app.adapters.sandbox.SandboxClientAdapter", ...)
    
    # Factories
    agent_factory = providers.Factory("app.factories.agent.AgentFactory", ...)
    flow_factory = providers.Factory("app.factories.flow.FlowFactory", ...)
```

### 4. Factories (`app/factories/`)

Object creation with dependency injection:

```python
# app/factories/agent.py
class AgentFactory:
    @inject
    def create_agent(
        self,
        agent_type: str,
        name: str,
        llm_provider: ILLMProvider = Provide[Container.llm_provider],
        logger: ILogger = Provide[Container.logger],
        config: IConfig = Provide[Container.app_config],
        sandbox_client: ISandboxClient = Provide[Container.sandbox_client]
    ) -> BaseAgent:
        # Creates agents with injected dependencies

# app/factories/flow.py
class FlowFactory:
    @inject
    def create_flow(self, flow_class: Type[BaseFlow], agents: ...) -> BaseFlow:
        # Creates flows with injected dependencies
```

### 5. Enhanced BaseAgent (`app/agent/base.py`)

Supports both old and new approaches:

```python
class BaseAgent:
    def __init__(
        self,
        name: str,
        # Optional DI parameters
        llm_provider: Optional[ILLMProvider] = None,
        logger: Optional[ILogger] = None,
        config: Optional[IConfig] = None,
        sandbox_client: Optional[ISandboxClient] = None
    ):
        # Store injected dependencies
        self._llm_provider = llm_provider
        self._logger = logger
        self._config = config
        self._sandbox_client = sandbox_client
    
    @classmethod
    def create_with_dependencies(
        cls,
        name: str,
        llm_provider: ILLMProvider,
        logger: ILogger,
        config: IConfig,
        sandbox_client: ISandboxClient
    ) -> "BaseAgent":
        # Factory method for DI creation
    
    @property
    def injected_logger(self) -> ILogger:
        # Returns injected logger or falls back to global
        return self._logger or logger
```

## Usage Examples

### Basic Usage

```python
# Create and configure container
container = Container.create_configured_container({
    "log": {"level": "INFO"},
    "llm": {"model": "gpt-4"},
    "workspace": {"root": "/path/to/workspace"}
})

# Wire modules for DI
container.wire_modules()

# Get factories
agent_factory = container.agent_factory()
flow_factory = container.flow_factory()

# Create agents with DI
agent = agent_factory.create_agent(
    agent_type="manus",
    name="my_agent"
)

# Create flows with DI
flow = flow_factory.create_simple_flow(
    agent_type="manus",
    agent_name="flow_agent"
)
```

### Backward Compatibility

```python
# Old way still works
from app.agent.manus import ManusAgent
old_agent = ManusAgent(name="old_style")

# New way with DI
new_agent = ManusAgent.create_with_dependencies(
    name="new_style",
    llm_provider=llm_provider,
    logger=logger,
    config=config,
    sandbox_client=sandbox_client
)
```

### Testing with Mocks

```python
from unittest.mock import Mock

# Create mocked dependencies
mock_llm = Mock()
mock_logger = Mock()
mock_config = Mock()
mock_sandbox = Mock()

# Create agent with mocks
test_agent = ManusAgent.create_with_dependencies(
    name="test",
    llm_provider=mock_llm,
    logger=mock_logger,
    config=mock_config,
    sandbox_client=mock_sandbox
)

# Test in isolation
test_agent.injected_logger.info("test")
mock_logger.info.assert_called_with("test")
```

## Configuration

### Environment Variables

```bash
# LLM Configuration
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Logging
LOG_LEVEL=INFO

# Workspace
WORKSPACE_ROOT=/path/to/workspace
```

### Configuration File

```yaml
# config.yaml
log:
  level: INFO
  correlation_id: "spark-session-123"

llm:
  model: gpt-4
  temperature: 0.7
  max_tokens: 4096
  api_key: ${OPENAI_API_KEY}
  base_url: ${OPENAI_BASE_URL}

workspace:
  root: /path/to/workspace
```

### Programmatic Configuration

```python
config_dict = {
    "log": {"level": "DEBUG"},
    "llm": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.3
    },
    "workspace": {"root": "/custom/path"}
}

container = Container.create_configured_container(config_dict)
```

## Benefits

### 1. **Testability**
- Easy to inject mocks for unit testing
- Isolated testing of components
- No global state dependencies in tests

### 2. **Modularity**
- Loose coupling between components
- Clear interfaces and contracts
- Easy to swap implementations

### 3. **Configurability**
- Centralized configuration management
- Environment-specific configurations
- Runtime configuration changes

### 4. **Backward Compatibility**
- Existing code continues to work
- Gradual migration path
- No breaking changes

### 5. **Scalability**
- Easy to add new dependencies
- Factory pattern for object creation
- Consistent dependency management

## Migration Guide

### For Existing Code

1. **No immediate changes required** - existing code continues to work
2. **Gradual adoption** - use new factories for new features
3. **Testing improvements** - use DI for better test isolation

### For New Code

1. **Use factories** - `AgentFactory` and `FlowFactory` for object creation
2. **Leverage DI** - inject dependencies instead of using globals
3. **Follow interfaces** - depend on abstractions, not concretions

### Best Practices

1. **Prefer factories** over direct instantiation
2. **Use interfaces** for type hints and dependencies
3. **Configure once** at application startup
4. **Wire modules** early in the application lifecycle
5. **Clean up** with `unwire_modules()` when needed

## Troubleshooting

### Common Issues

1. **Module not wired**: Ensure module is in `wiring_config.modules`
2. **Circular imports**: Use string references in providers
3. **Missing dependencies**: Check container configuration
4. **Type errors**: Ensure proper interface implementations

### Debug Tips

1. **Enable debug logging**: Set `LOG_LEVEL=DEBUG`
2. **Check container state**: Use `container.check_dependencies()`
3. **Verify wiring**: Ensure `wire_modules()` is called
4. **Test isolation**: Use mocks to isolate components

## Future Enhancements

1. **Configuration validation** - Schema validation for config
2. **Health checks** - Built-in health check endpoints
3. **Metrics integration** - Dependency injection for metrics
4. **Plugin system** - Dynamic dependency registration
5. **Performance monitoring** - Injection performance tracking