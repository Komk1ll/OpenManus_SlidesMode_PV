"""Performance tests for Dependency Injection architecture.

These tests ensure the DI system performs well under various conditions
and is ready for production workloads.
"""

import pytest
import asyncio
import time
import threading
import concurrent.futures
from unittest.mock import Mock, AsyncMock
from typing import List, Dict, Any
import psutil
import gc
import sys

from app.container import Container
from app.factories.agent import AgentFactory
from app.factories.flow import FlowFactory
from app.interfaces.llm import ILLMProvider
from app.interfaces.logger import ILogger
from app.interfaces.config import IConfig
from app.interfaces.sandbox import ISandboxClient


class PerformanceMonitor:
    """Monitor system performance during tests."""
    
    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.process = psutil.Process()
    
    def start(self):
        """Start monitoring."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
        gc.collect()  # Clean up before measurement
    
    def stop(self) -> Dict[str, float]:
        """Stop monitoring and return metrics."""
        end_time = time.time()
        end_memory = self.process.memory_info().rss
        
        return {
            'duration': end_time - self.start_time,
            'memory_delta_mb': (end_memory - self.start_memory) / 1024 / 1024,
            'peak_memory_mb': self.process.memory_info().peak_wss / 1024 / 1024 if hasattr(self.process.memory_info(), 'peak_wss') else 0
        }


@pytest.fixture
def performance_container():
    """Create a container optimized for performance testing."""
    container = Container()
    
    # Use lightweight mocks for performance testing
    mock_llm = Mock(spec=ILLMProvider)
    mock_llm.generate_response = AsyncMock(return_value="Fast response")
    mock_llm.generate_structured_response = AsyncMock(return_value={"result": "fast"})
    
    mock_logger = Mock(spec=ILogger)
    mock_logger.info = Mock()
    mock_logger.error = Mock()
    mock_logger.debug = Mock()
    
    mock_config = Mock(spec=IConfig)
    mock_config.get = Mock(return_value="fast_value")
    mock_config.get_section = Mock(return_value={"key": "value"})
    
    mock_sandbox = Mock(spec=ISandboxClient)
    mock_sandbox.cleanup = AsyncMock()
    mock_sandbox.execute = AsyncMock(return_value="fast_execution")
    
    # Override with fast mocks
    container.llm_provider.override(mock_llm)
    container.logger.override(mock_logger)
    container.config.override(mock_config)
    container.sandbox_client.override(mock_sandbox)
    
    return container


class TestContainerPerformance:
    """Test container creation and wiring performance."""
    
    def test_container_creation_speed(self):
        """Test container creation performance."""
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Create multiple containers
        containers = []
        for _ in range(100):
            container = Container()
            containers.append(container)
        
        metrics = monitor.stop()
        
        # Assert performance requirements
        assert metrics['duration'] < 1.0, f"Container creation too slow: {metrics['duration']:.3f}s"
        assert metrics['memory_delta_mb'] < 50, f"Too much memory used: {metrics['memory_delta_mb']:.2f}MB"
        assert len(containers) == 100
    
    def test_wiring_performance(self, performance_container):
        """Test module wiring performance."""
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Wire and unwire multiple times
        for _ in range(50):
            performance_container.wire(modules=["app.factories.agent", "app.factories.flow"])
            performance_container.unwire()
        
        metrics = monitor.stop()
        
        assert metrics['duration'] < 2.0, f"Wiring too slow: {metrics['duration']:.3f}s"
    
    def test_provider_resolution_speed(self, performance_container):
        """Test dependency resolution performance."""
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Resolve dependencies many times
        for _ in range(1000):
            llm = performance_container.llm_provider()
            logger = performance_container.logger()
            config = performance_container.config()
            sandbox = performance_container.sandbox_client()
            
            # Verify they're not None
            assert llm is not None
            assert logger is not None
            assert config is not None
            assert sandbox is not None
        
        metrics = monitor.stop()
        
        assert metrics['duration'] < 1.0, f"Provider resolution too slow: {metrics['duration']:.3f}s"


class TestFactoryPerformance:
    """Test factory performance."""
    
    def test_agent_creation_speed(self, performance_container):
        """Test agent creation performance."""
        agent_factory = performance_container.agent_factory()
        
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Create many agents
        agents = []
        for _ in range(100):
            agent = agent_factory.create_manus_agent()
            agents.append(agent)
        
        metrics = monitor.stop()
        
        assert metrics['duration'] < 2.0, f"Agent creation too slow: {metrics['duration']:.3f}s"
        assert len(agents) == 100
        
        # Verify all agents have DI components
        for agent in agents[:10]:  # Check first 10 to avoid too much overhead
            assert hasattr(agent, '_llm_provider')
            assert hasattr(agent, '_logger')
    
    def test_different_agent_types_performance(self, performance_container):
        """Test creation of different agent types."""
        agent_factory = performance_container.agent_factory()
        
        agent_creators = [
            agent_factory.create_manus_agent,
            agent_factory.create_swe_agent,
            agent_factory.create_browser_agent,
            agent_factory.create_mcp_agent,
            agent_factory.create_toolcall_agent
        ]
        
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Create 20 of each type
        all_agents = []
        for creator in agent_creators:
            for _ in range(20):
                agent = creator()
                all_agents.append(agent)
        
        metrics = monitor.stop()
        
        assert metrics['duration'] < 3.0, f"Multi-type creation too slow: {metrics['duration']:.3f}s"
        assert len(all_agents) == 100  # 5 types * 20 each
    
    def test_flow_creation_performance(self, performance_container):
        """Test flow creation performance."""
        flow_factory = performance_container.flow_factory()
        
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Create many flows
        flows = []
        for i in range(50):
            simple_flow = flow_factory.create_simple_flow(f"agent_{i}")
            multi_flow = flow_factory.create_multi_agent_flow([f"agent_{i}_1", f"agent_{i}_2"])
            flows.extend([simple_flow, multi_flow])
        
        metrics = monitor.stop()
        
        assert metrics['duration'] < 2.0, f"Flow creation too slow: {metrics['duration']:.3f}s"
        assert len(flows) == 100


class TestConcurrencyPerformance:
    """Test concurrent access performance."""
    
    def test_concurrent_container_access(self, performance_container):
        """Test concurrent access to container."""
        def create_agent():
            agent_factory = performance_container.agent_factory()
            return agent_factory.create_manus_agent()
        
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Create agents concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_agent) for _ in range(100)]
            agents = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        metrics = monitor.stop()
        
        assert metrics['duration'] < 5.0, f"Concurrent creation too slow: {metrics['duration']:.3f}s"
        assert len(agents) == 100
    
    @pytest.mark.asyncio
    async def test_async_operations_performance(self, performance_container):
        """Test async operations performance."""
        agent_factory = performance_container.agent_factory()
        
        async def create_and_run_agent():
            agent = agent_factory.create_manus_agent()
            # Simulate some async work
            await agent.injected_llm_provider.generate_response("test")
            return agent
        
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Run many async operations
        tasks = [create_and_run_agent() for _ in range(50)]
        agents = await asyncio.gather(*tasks)
        
        metrics = monitor.stop()
        
        assert metrics['duration'] < 3.0, f"Async operations too slow: {metrics['duration']:.3f}s"
        assert len(agents) == 50
    
    def test_thread_safety_performance(self, performance_container):
        """Test thread safety doesn't impact performance significantly."""
        results = []
        
        def worker():
            start = time.time()
            agent_factory = performance_container.agent_factory()
            for _ in range(10):
                agent = agent_factory.create_manus_agent()
                assert agent is not None
            end = time.time()
            results.append(end - start)
        
        # Run multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
        
        start_time = time.time()
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        assert total_time < 5.0, f"Thread safety overhead too high: {total_time:.3f}s"
        assert len(results) == 10
        
        # Check that no thread took too long
        max_thread_time = max(results)
        assert max_thread_time < 2.0, f"Individual thread too slow: {max_thread_time:.3f}s"


class TestMemoryPerformance:
    """Test memory usage and cleanup."""
    
    def test_memory_usage_agent_creation(self, performance_container):
        """Test memory usage during agent creation."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create many agents
        agents = []
        agent_factory = performance_container.agent_factory()
        
        for _ in range(100):
            agent = agent_factory.create_manus_agent()
            agents.append(agent)
        
        peak_memory = process.memory_info().rss
        memory_increase = (peak_memory - initial_memory) / 1024 / 1024  # MB
        
        # Clean up
        del agents
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_after_cleanup = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Assert reasonable memory usage
        assert memory_increase < 100, f"Too much memory used: {memory_increase:.2f}MB"
        assert memory_after_cleanup < memory_increase / 2, "Memory not properly cleaned up"
    
    def test_container_memory_cleanup(self):
        """Test container memory cleanup."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        containers = []
        for _ in range(50):
            container = Container()
            container.wire(modules=["app.factories.agent"])
            containers.append(container)
        
        peak_memory = process.memory_info().rss
        
        # Cleanup containers
        for container in containers:
            container.unwire()
        del containers
        gc.collect()
        
        final_memory = process.memory_info().rss
        
        memory_increase = (peak_memory - initial_memory) / 1024 / 1024
        memory_after_cleanup = (final_memory - initial_memory) / 1024 / 1024
        
        assert memory_increase < 50, f"Container memory usage too high: {memory_increase:.2f}MB"
        assert memory_after_cleanup < memory_increase / 2, "Container memory not cleaned up"


class TestScalabilityPerformance:
    """Test scalability characteristics."""
    
    @pytest.mark.parametrize("agent_count", [10, 50, 100, 200])
    def test_scaling_agent_creation(self, performance_container, agent_count):
        """Test how performance scales with number of agents."""
        agent_factory = performance_container.agent_factory()
        
        start_time = time.time()
        
        agents = []
        for _ in range(agent_count):
            agent = agent_factory.create_manus_agent()
            agents.append(agent)
        
        duration = time.time() - start_time
        
        # Performance should scale roughly linearly
        time_per_agent = duration / agent_count
        
        assert time_per_agent < 0.02, f"Time per agent too high: {time_per_agent:.4f}s"
        assert len(agents) == agent_count
    
    def test_large_scale_container_operations(self, performance_container):
        """Test large scale operations."""
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Simulate large scale usage
        operations = 0
        
        # Create many different components
        for _ in range(100):
            agent_factory = performance_container.agent_factory()
            flow_factory = performance_container.flow_factory()
            
            agent = agent_factory.create_manus_agent()
            flow = flow_factory.create_simple_flow("test")
            
            operations += 2
        
        metrics = monitor.stop()
        
        operations_per_second = operations / metrics['duration']
        
        assert operations_per_second > 50, f"Operations per second too low: {operations_per_second:.2f}"
        assert metrics['memory_delta_mb'] < 100, f"Memory usage too high: {metrics['memory_delta_mb']:.2f}MB"


if __name__ == "__main__":
    # Run performance tests
    pytest.main([
        __file__,
        "-v",
        "-m", "not slow",
        "--durations=10"
    ])