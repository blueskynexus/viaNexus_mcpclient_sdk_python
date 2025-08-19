import asyncio
import logging
from vianexus_agent_sdk.clients.anthropic_client import AnthropicClient

async def main():
    try:
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        
        # Create the client - config is automatically loaded from config.yaml!
        client = AnthropicClient()  # No config needed!
        
        # Connect and run - handles all the connection setup internally
        await client.connect_and_run()
        
    except Exception as e:
        logging.error(f"Setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
