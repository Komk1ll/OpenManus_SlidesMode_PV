"""Example demonstrating dependency injection usage in Spark.

This example shows how to use the new DI-based architecture
to create agents and flows with proper dependency injection.
"""

import asyncio
from pathlib import Path

from app.container import Container
from app.factories.agent import AgentFactory
from app.factories.flow import FlowFactory
from app.agent.base import BaseAgent


async def example_basic_di_usage():
    """Basic example of using dependency injection."""
    print("=== Basic Dependency Injection Usage ===")
    
    # Create and configure container
    container = Container.create_configured_container({
        "log": {"level": "INFO"},
        "llm": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2048
        },
        "workspace": {"root": str(Path.cwd())}
    })
    
    # Wire modules for dependency injection
    container.wire_modules()
    
    try:
        # Get factories from container
        agent_factory = container.agent_factory()
        flow_factory = container.flow_factory()
        
        # Create agents using DI
        manus_agent = agent_factory.create_agent(
            agent_type="manus",
            name="manus_di_example"
        )
        
        swe_agent = agent_factory.create_agent(
            agent_type="swe", 
            name="swe_di_example"
        )
        
        print(f"Created agents: {manus_agent.name}, {swe_agent.name}")
        
        # Create a simple flow
        simple_flow = flow_factory.create_simple_flow(
            agent_type="manus",
            agent_name="simple_flow_agent"
        )
        
        print(f"Created simple flow with agent: {list(simple_flow.agents.keys())}")
        
        # Create multi-agent flow
        multi_flow = flow_factory.create_multi_agent_flow(
            agent_configs={
                "primary": "manus",
                "assistant": "swe",
                "browser": "browser"
            },
            primary_agent_key="primary"
        )
        
        print(f"Created multi-agent flow with agents: {list(multi_flow.agents.keys())}")
        
    finally:
        # Clean up
        container.unwire_modules()


async def example_backward_compatibility():
    """Example showing backward compatibility with existing code."""
    print("\n=== Backward Compatibility Example ===")
    
    # Import existing agent classes
    from app.agent.manus import ManusAgent
    from app.agent.swe import SWEAgent
    
    # Create agents the old way (still works)
    old_manus = ManusAgent(name="old_manus")
    old_swe = SWEAgent(name="old_swe")
    
    print(f"Created agents old way: {old_manus.name}, {old_swe.name}")
    
    # Create agents with DI using the new factory method
    container = Container.create_configured_container()
    container.wire_modules()
    
    try:
        # Get dependencies from container
        llm_provider = container.llm_provider()
        logger = container.logger()
        config = container.app_config()
        sandbox_client = container.sandbox_client()
        
        # Create agents with DI
        new_manus = ManusAgent.create_with_dependencies(
            name="new_manus",
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client
        )
        
        new_swe = SWEAgent.create_with_dependencies(
            name="new_swe",
            llm_provider=llm_provider,
            logger=logger,
            config=config,
            sandbox_client=sandbox_client
        )
        
        print(f"Created agents with DI: {new_manus.name}, {new_swe.name}")
        
        # Both approaches work and can be mixed
        print("Both old and new approaches work side by side!")
        
    finally:
        container.unwire_modules()


async def example_custom_configuration():
    """Example with custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    # Custom configuration
    custom_config = {
        "log": {
            "level": "DEBUG",
            "correlation_id": "example-123"
        },
        "llm": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.3,
            "max_tokens": 1024
        },
        "workspace": {
            "root": "/tmp/spark_workspace"
        }
    }
    
    container = Container.create_configured_container(custom_config)
    container.wire_modules()
    
    try:
        # Create factory with custom config
        agent_factory = container.agent_factory()
        
        # Create agent - it will use the custom configuration
        agent = agent_factory.create_agent(
            agent_type="manus",
            name="custom_config_agent"
        )
        
        print(f"Created agent with custom config: {agent.name}")
        print(f"Agent uses injected dependencies with custom settings")
        
    finally:
        container.unwire_modules()


async def example_testing_with_mocks():
    """Example showing how to use DI for testing with mocks."""
    print("\n=== Testing with Mocks Example ===")
    
    # This would typically be in a test file
    from unittest.mock import Mock
    
    # Create mock dependencies
    mock_llm = Mock()
    mock_logger = Mock()
    mock_config = Mock()
    mock_sandbox = Mock()
    
    # Import agent class
    from app.agent.manus import ManusAgent
    
    # Create agent with mocked dependencies
    test_agent = ManusAgent.create_with_dependencies(
        name="test_agent",
        llm_provider=mock_llm,
        logger=mock_logger,
        config=mock_config,
        sandbox_client=mock_sandbox
    )
    
    print(f"Created test agent with mocked dependencies: {test_agent.name}")
    print("This enables isolated unit testing!")
    
    # Verify mocks can be used
    test_agent.injected_logger.info("Test message")
    mock_logger.info.assert_called_with("Test message")
    print("Mock verification successful!")


async def main():
    """Run all examples."""
    print("Spark Dependency Injection Examples")
    print("===================================\n")
    
    await example_basic_di_usage()
    await example_backward_compatibility()
    await example_custom_configuration()
    await example_testing_with_mocks()
    
    print("\n=== All Examples Completed ===")
    print("\nKey Benefits of the New DI Architecture:")
    print("1. ✅ Backward compatibility - existing code still works")
    print("2. ✅ Testability - easy to inject mocks for testing")
    print("3. ✅ Configurability - centralized configuration management")
    print("4. ✅ Modularity - loose coupling between components")
    print("5. ✅ Scalability - easy to add new dependencies")
    print("6. ✅ Factory pattern - simplified object creation")


if __name__ == "__main__":
    asyncio.run(main())