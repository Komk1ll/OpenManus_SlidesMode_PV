#!/usr/bin/env python3
"""
Simple test for presentation agent functionality
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_presentation_agent():
    """Test the presentation agent with a simple topic"""
    try:
        # Import after setting up path
        from app.agent.presentation_agent import PresentationAgent, PresentationConfig
        
        logger.info("Creating presentation agent...")
        
        # Create configuration for first presentation
        config = PresentationConfig(
            topic="Искусственный интеллект в образовании",
            slide_count=5,
            language="russian"
        )
        
        # Create agent
        agent = PresentationAgent()
        
        logger.info(f"Starting presentation creation for topic: {config.topic}")
        
        # Create presentation
        result = await agent.create_presentation(config)
        
        if result and not result.error:
            logger.info("✅ Presentation created successfully!")
            logger.info(f"Result: {result.output}")
            return True
        else:
            logger.error(f"❌ Presentation creation failed: {result.error if result else 'No result'}")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

async def test_basic_imports():
    """Test basic imports work"""
    try:
        from app.tool.base import ToolResult
        from app.agent.presentation_agent import PresentationAgent
        
        logger.info("✅ Basic imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Import test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("Starting OpenManus presentation agent tests...")
    
    # Test 1: Basic imports
    if not await test_basic_imports():
        return
    
    # Test 2: Presentation agent functionality
    await test_presentation_agent()
    
    logger.info("Tests completed.")

if __name__ == "__main__":
    asyncio.run(main())

