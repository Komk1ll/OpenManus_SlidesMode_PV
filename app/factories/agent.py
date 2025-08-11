"""Agent factory with dependency injection support."""

from typing import Dict, Type, Any, Optional, TYPE_CHECKING
from dependency_injector.wiring import inject, Provide

from app.agent.base import BaseAgent
from app.agent.manus import Manus
from app.agent.swe import SWEAgent
from app.agent.browser import BrowserAgent
from app.agent.mcp import MCPAgent
from app.agent.toolcall import ToolCallAgent
from app.interfaces.llm import ILLMProvider
from app.interfaces.logger import ILogger
from app.interfaces.config import IConfig
from app.interfaces.sandbox import ISandboxClient


class AgentFactory:
    """Factory for creating agents with dependency injection.
    
    This factory uses the dependency injection container to create agents
    with properly injected dependencies, following the @inject pattern.
    """
    
    # Registry of available agent types
    AGENT_TYPES: Dict[str, Type[BaseAgent]] = {
        "manus": Manus,
        "swe": SWEAgent,
        "browser": BrowserAgent,
        "mcp": MCPAgent,
        "toolcall": ToolCallAgent,
    }
    
    @inject
    def create_agent(
        self,
        agent_type: str,
        name: Optional[str] = None,
        llm_provider: ILLMProvider = Provide["llm_provider"],
        logger: ILogger = Provide["logger"],
        config: IConfig = Provide["app_config"],
        sandbox_client: ISandboxClient = Provide["sandbox_client"],
        **kwargs: Any
    ) -> BaseAgent:
        """Create an agent with injected dependencies.
        
        Args:
            agent_type: Type of agent to create (e.g., 'manus', 'swe', 'browser')
            name: Optional custom name for the agent
            llm_provider: Injected LLM provider
            logger: Injected logger
            config: Injected configuration
            sandbox_client: Injected sandbox client
            **kwargs: Additional agent-specific parameters
            
        Returns:
            Configured agent instance with injected dependencies
            
        Raises:
            ValueError: If agent_type is not supported
        """
        if agent_type not in self.AGENT_TYPES:
            available_types = ", ".join(self.AGENT_TYPES.keys())
            raise ValueError(
                f"Unsupported agent type: {agent_type}. "
                f"Available types: {available_types}"
            )
        
        agent_class = self.AGENT_TYPES[agent_type]
        
        # Set default name if not provided
        if name is None:
            name = agent_type
        
        # Create agent with DI dependencies
        agent = agent_class.create_with_dependencies(
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client,
            name=name,
            **kwargs
        )
        
        logger.info(f"Created {agent_type} agent '{name}' with injected dependencies")
        return agent
    
    @inject
    def create_manus_agent(
        self,
        name: str = "manus",
        llm_provider: ILLMProvider = Provide["llm_provider"],
        logger: ILogger = Provide["logger"],
        config: IConfig = Provide["app_config"],
        sandbox_client: ISandboxClient = Provide["sandbox_client"],
        **kwargs: Any
    ) -> Manus:
        """Create a Manus agent with injected dependencies.
        
        Args:
            name: Agent name
            llm_provider: Injected LLM provider
            logger: Injected logger
            config: Injected configuration
            sandbox_client: Injected sandbox client
            **kwargs: Additional Manus-specific parameters
            
        Returns:
            Configured Manus agent
        """
        return self.create_agent(
            agent_type="manus",
            name=name,
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client,
            **kwargs
        )
    
    @inject
    def create_swe_agent(
        self,
        name: str = "swe",
        llm_provider: ILLMProvider = Provide["llm_provider"],
        logger: ILogger = Provide["logger"],
        config: IConfig = Provide["app_config"],
        sandbox_client: ISandboxClient = Provide["sandbox_client"],
        **kwargs: Any
    ) -> SWEAgent:
        """Create a SWE agent with injected dependencies.
        
        Args:
            name: Agent name
            llm_provider: Injected LLM provider
            logger: Injected logger
            config: Injected configuration
            sandbox_client: Injected sandbox client
            **kwargs: Additional SWE-specific parameters
            
        Returns:
            Configured SWE agent
        """
        return self.create_agent(
            agent_type="swe",
            name=name,
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client,
            **kwargs
        )
    
    @inject
    def create_browser_agent(
        self,
        name: str = "browser",
        llm_provider: ILLMProvider = Provide["llm_provider"],
        logger: ILogger = Provide["logger"],
        config: IConfig = Provide["app_config"],
        sandbox_client: ISandboxClient = Provide["sandbox_client"],
        **kwargs: Any
    ) -> BrowserAgent:
        """Create a Browser agent with injected dependencies.
        
        Args:
            name: Agent name
            llm_provider: Injected LLM provider
            logger: Injected logger
            config: Injected configuration
            sandbox_client: Injected sandbox client
            **kwargs: Additional Browser-specific parameters
            
        Returns:
            Configured Browser agent
        """
        return self.create_agent(
            agent_type="browser",
            name=name,
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client,
            **kwargs
        )
    
    def get_available_agent_types(self) -> list[str]:
        """Get list of available agent types.
        
        Returns:
            List of supported agent type names
        """
        return list(self.AGENT_TYPES.keys())
    
    @inject
    def create_mcp_agent(
        self,
        name: str = "mcp",
        llm_provider: ILLMProvider = Provide["llm_provider"],
        logger: ILogger = Provide["logger"],
        config: IConfig = Provide["app_config"],
        sandbox_client: ISandboxClient = Provide["sandbox_client"],
        **kwargs: Any
    ) -> MCPAgent:
        """Create an MCP agent with injected dependencies.
        
        Args:
            name: Agent name
            llm_provider: Injected LLM provider
            logger: Injected logger
            config: Injected configuration
            sandbox_client: Injected sandbox client
            **kwargs: Additional MCP-specific parameters
            
        Returns:
            Configured MCP agent
        """
        return self.create_agent(
            agent_type="mcp",
            name=name,
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client,
            **kwargs
        )
    
    @inject
    def create_toolcall_agent(
        self,
        name: str = "toolcall",
        llm_provider: ILLMProvider = Provide["llm_provider"],
        logger: ILogger = Provide["logger"],
        config: IConfig = Provide["app_config"],
        sandbox_client: ISandboxClient = Provide["sandbox_client"],
        **kwargs: Any
    ) -> ToolCallAgent:
        """Create a ToolCall agent with injected dependencies.
        
        Args:
            name: Agent name
            llm_provider: Injected LLM provider
            logger: Injected logger
            config: Injected configuration
            sandbox_client: Injected sandbox client
            **kwargs: Additional ToolCall-specific parameters
            
        Returns:
            Configured ToolCall agent
        """
        return self.create_agent(
            agent_type="toolcall",
            name=name,
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client,
            **kwargs
        )