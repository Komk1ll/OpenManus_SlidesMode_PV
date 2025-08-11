"""Dependency Injection Container for the Spark application."""

import os
from pathlib import Path
from typing import Dict, Any

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from app.interfaces import ILLMProvider, ILogger, IConfig, ISandboxClient
from app.schema import Memory


class Container(containers.DeclarativeContainer):
    """Main dependency injection container.
    
    Manages all application dependencies including:
    - Configuration
    - Logging
    - LLM providers
    - Sandbox clients
    - Agent factories
    """

    # Wiring configuration for automatic dependency injection
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.agent",
            "app.flow", 
            "app.llm",
            "app.factories.agent",
            "app.factories.flow",
            "__main__",
        ]
    )

    # Configuration provider
    config = providers.Configuration()

    # Core services
    logger = providers.Singleton(
        "app.adapters.logger.StructuredLogger",
        level=config.log.level.as_(str, default="INFO"),
        correlation_id=config.log.correlation_id.as_(str, default=""),
    )

    app_config = providers.Singleton(
        "app.adapters.config.AppConfig",
        workspace_root=config.workspace.root.as_(str, default=str(Path.cwd())),
        log_level=config.log.level.as_(str, default="INFO"),
    )

    # LLM provider factory
    llm_provider = providers.Factory(
        "app.adapters.llm.OpenAIProvider",
        config_name=config.llm.config_name.as_(str, default="default"),
        llm_config=config.llm.as_(dict, default={}),
    )

    # Sandbox client
    sandbox_client = providers.Singleton(
        "app.adapters.sandbox.SandboxClientAdapter",
        logger=logger,
        config=app_config,
    )

    # Memory factory
    memory_factory = providers.Factory(
        Memory,
    )

    # Agent factory
    agent_factory = providers.Factory(
        "app.factories.agent.AgentFactory",
        llm_provider=llm_provider,
        logger=logger,
        config=app_config,
        sandbox_client=sandbox_client,
        memory_factory=memory_factory,
    )

    # Flow factory
    flow_factory = providers.Factory(
        "app.factories.flow.FlowFactory",
        agent_factory=agent_factory,
        logger=logger,
        config=app_config,
    )

    @classmethod
    def create_configured_container(
        cls, 
        config_dict: Dict[str, Any] = None,
        config_file: str = None
    ) -> "Container":
        """Create a configured container instance.
        
        Args:
            config_dict: Configuration dictionary
            config_file: Path to configuration file
            
        Returns:
            Configured container instance
        """
        container = cls()
        
        # Load configuration from file if provided
        if config_file and os.path.exists(config_file):
            container.config.from_yaml(config_file)
        
        # Override with dictionary config if provided
        if config_dict:
            container.config.from_dict(config_dict)
        
        # Load from environment variables
        container.config.llm.api_key.from_env("OPENAI_API_KEY", default="")
        container.config.llm.base_url.from_env("OPENAI_BASE_URL", default="")
        container.config.llm.model.from_env("OPENAI_MODEL", default="gpt-4")
        container.config.log.level.from_env("LOG_LEVEL", default="INFO")
        container.config.workspace.root.from_env("WORKSPACE_ROOT", default=str(Path.cwd()))
        
        return container

    def wire_modules(self) -> None:
        """Wire all configured modules for dependency injection."""
        self.wire(modules=self.wiring_config.modules)

    def unwire_modules(self) -> None:
        """Unwire all modules (useful for testing)."""
        self.unwire()