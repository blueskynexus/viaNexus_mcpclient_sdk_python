import asyncio
import logging
from dotenv import load_dotenv
from vianexus_agent_sdk.clients.anthropic_client import AnthropicClient
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tools.get_config import get_config

load_dotenv()  # load environment variables from .env

async def main():
    try:
        # Load the config file
        config = get_config(env="development")
        logging.basicConfig(level=config["LOG_LEVEL"])
        
        # Create the client with config - much simpler!
        client = AnthropicClient(config)
        
        # Connect and run - handles all the connection setup internally
        await client.connect_and_run()
        
    except Exception as e:
        logging.error(f"Setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
