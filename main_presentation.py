import argparse
import asyncio
import os

from app.agent.presentation_agent import PresentationAgent
from app.logger import logger


async def main():
    # Set environment variables for API keys
    os.environ['TAVILY_API_KEY'] = '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'
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Manus agent with presentation support")
    parser.add_argument(
        "--prompt", type=str, required=False, help="Input prompt for the agent"
    )
    args = parser.parse_args()

    # Create and initialize Presentation agent
    agent = await PresentationAgent.create()
    try:
        # Use command line prompt if provided, otherwise ask for input
        prompt = args.prompt if args.prompt else input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")
        await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        # Ensure agent resources are cleaned up before exiting
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

