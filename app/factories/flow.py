"""Flow factory with dependency injection support."""

from typing import Dict, Type, Any, Optional, List, Union
from dependency_injector.wiring import inject, Provide

from app.flow.base import BaseFlow
from app.agent.base import BaseAgent
from app.factories.agent import AgentFactory
from app.interfaces.llm import ILLMProvider
from app.interfaces.logger import ILogger
from app.interfaces.config import IConfig
from app.interfaces.sandbox import ISandboxClient


class FlowFactory:
    """Factory for creating flows with dependency injection.
    
    This factory creates flows with properly injected dependencies
    and can automatically create agents for the flows using AgentFactory.
    """
    
    @inject
    def __init__(
        self,
        agent_factory: AgentFactory = Provide["agent_factory"],
        logger: ILogger = Provide["logger"]
    ):
        """Initialize flow factory with injected dependencies.
        
        Args:
            agent_factory: Injected agent factory for creating agents
            logger: Injected logger
        """
        self.agent_factory = agent_factory
        self.logger = logger
    
    @inject
    def create_flow(
        self,
        flow_class: Type[BaseFlow],
        agents: Union[BaseAgent, List[BaseAgent], Dict[str, BaseAgent], List[str], Dict[str, str]],
        primary_agent_key: Optional[str] = None,
        llm_provider: ILLMProvider = Provide["llm_provider"],
        logger: ILogger = Provide["logger"],
        config: IConfig = Provide["app_config"],
        sandbox_client: ISandboxClient = Provide["sandbox_client"],
        **kwargs: Any
    ) -> BaseFlow:
        """Create a flow with injected dependencies.
        
        Args:
            flow_class: The flow class to instantiate
            agents: Agents for the flow - can be:
                - BaseAgent instance
                - List of BaseAgent instances
                - Dict mapping keys to BaseAgent instances
                - List of agent type strings (will create agents)
                - Dict mapping keys to agent type strings (will create agents)
            primary_agent_key: Key of the primary agent
            llm_provider: Injected LLM provider
            logger: Injected logger
            config: Injected configuration
            sandbox_client: Injected sandbox client
            **kwargs: Additional flow-specific parameters
            
        Returns:
            Configured flow instance
        """
        # Process agents parameter
        processed_agents = self._process_agents(
            agents, llm_provider, logger, config, sandbox_client
        )
        
        # Create flow instance
        flow = flow_class(
            agents=processed_agents,
            primary_agent_key=primary_agent_key,
            **kwargs
        )
        
        logger.info(f"Created {flow_class.__name__} flow with {len(processed_agents)} agents")
        return flow
    
    def _process_agents(
        self,
        agents: Union[BaseAgent, List[BaseAgent], Dict[str, BaseAgent], List[str], Dict[str, str]],
        llm_provider: ILLMProvider,
        logger: ILogger,
        config: IConfig,
        sandbox_client: ISandboxClient
    ) -> Dict[str, BaseAgent]:
        """Process agents parameter into a dictionary of BaseAgent instances.
        
        Args:
            agents: Various agent specifications
            llm_provider: LLM provider for creating new agents
            logger: Logger for creating new agents
            config: Config for creating new agents
            sandbox_client: Sandbox client for creating new agents
            
        Returns:
            Dictionary mapping agent keys to BaseAgent instances
        """
        if isinstance(agents, BaseAgent):
            # Single agent
            return {"primary": agents}
        
        elif isinstance(agents, list):
            if all(isinstance(agent, BaseAgent) for agent in agents):
                # List of BaseAgent instances
                return {f"agent_{i}": agent for i, agent in enumerate(agents)}
            elif all(isinstance(agent_type, str) for agent_type in agents):
                # List of agent type strings
                result = {}
                for i, agent_type in enumerate(agents):
                    agent = self.agent_factory.create_agent(
                        agent_type=agent_type,
                        name=f"{agent_type}_{i}",
                        llm_provider=llm_provider,
                        logger=logger,
                        config=config,
                        sandbox_client=sandbox_client
                    )
                    result[f"agent_{i}"] = agent
                return result
            else:
                raise ValueError("List must contain either all BaseAgent instances or all strings")
        
        elif isinstance(agents, dict):
            if all(isinstance(agent, BaseAgent) for agent in agents.values()):
                # Dict of BaseAgent instances
                return agents
            elif all(isinstance(agent_type, str) for agent_type in agents.values()):
                # Dict of agent type strings
                result = {}
                for key, agent_type in agents.items():
                    agent = self.agent_factory.create_agent(
                        agent_type=agent_type,
                        name=key,
                        llm_provider=llm_provider,
                        logger=logger,
                        config=config,
                        sandbox_client=sandbox_client
                    )
                    result[key] = agent
                return result
            else:
                raise ValueError("Dict values must be either all BaseAgent instances or all strings")
        
        else:
            raise ValueError(
                "agents must be BaseAgent, List[BaseAgent], Dict[str, BaseAgent], "
                "List[str], or Dict[str, str]"
            )
    
    @inject
    def create_simple_flow(
        self,
        agent_type: str,
        agent_name: Optional[str] = None,
        llm_provider: ILLMProvider = Provide["llm_provider"],
        logger: ILogger = Provide["logger"],
        config: IConfig = Provide["app_config"],
        sandbox_client: ISandboxClient = Provide["sandbox_client"],
        **kwargs: Any
    ) -> BaseFlow:
        """Create a simple flow with a single agent.
        
        Args:
            agent_type: Type of agent to create
            agent_name: Optional name for the agent
            llm_provider: Injected LLM provider
            logger: Injected logger
            config: Injected configuration
            sandbox_client: Injected sandbox client
            **kwargs: Additional flow parameters
            
        Returns:
            Simple flow with one agent
        """
        # Import here to avoid circular imports
        from app.flow.simple import SimpleFlow
        
        agent = self.agent_factory.create_agent(
            agent_type=agent_type,
            name=agent_name or agent_type,
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client
        )
        
        return SimpleFlow(
            agents={"primary": agent},
            primary_agent_key="primary",
            **kwargs
        )
    
    @inject
    def create_multi_agent_flow(
        self,
        agent_configs: Dict[str, str],
        primary_agent_key: str,
        llm_provider: ILLMProvider = Provide["llm_provider"],
        logger: ILogger = Provide["logger"],
        config: IConfig = Provide["app_config"],
        sandbox_client: ISandboxClient = Provide["sandbox_client"],
        **kwargs: Any
    ) -> BaseFlow:
        """Create a multi-agent flow.
        
        Args:
            agent_configs: Dict mapping agent keys to agent types
            primary_agent_key: Key of the primary agent
            llm_provider: Injected LLM provider
            logger: Injected logger
            config: Injected configuration
            sandbox_client: Injected sandbox client
            **kwargs: Additional flow parameters
            
        Returns:
            Multi-agent flow
        """
        # Import here to avoid circular imports
        from app.flow.multi_agent import MultiAgentFlow
        
        return self.create_flow(
            flow_class=MultiAgentFlow,
            agents=agent_configs,
            primary_agent_key=primary_agent_key,
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client,
            **kwargs
        )