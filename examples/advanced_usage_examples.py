import asyncio
import logging
from vianexus_agent_sdk.clients.anthropic_client import AnthropicClient
from vianexus_agent_sdk.clients.openai_client import OpenAiClient

async def example_auto_config():
    """Example 1: Automatic config loading from config.yaml"""
    logging.info("=== Example 1: Auto-config loading ===")
    
    try:
        # Simplest usage - automatically finds and loads config.yaml
        client = AnthropicClient()
        await client.connect_and_run()
    except Exception as e:
        logging.error(f"Auto-config example failed: {e}")

async def example_custom_environment():
    """Example 2: Load config from a specific environment"""
    logging.info("=== Example 2: Custom environment ===")
    
    try:
        # Load from 'production' environment instead of 'development'
        client = AnthropicClient(env="production")
        await client.connect_and_run()
    except Exception as e:
        logging.error(f"Custom environment example failed: {e}")

async def example_custom_config_path():
    """Example 3: Load config from a custom path"""
    logging.info("=== Example 3: Custom config path ===")
    
    try:
        # Load from a different config file
        client = AnthropicClient(config_path="my_config.yaml", env="staging")
        await client.connect_and_run()
    except Exception as e:
        logging.error(f"Custom config path example failed: {e}")

async def example_explicit_config():
    """Example 4: Pass config explicitly (for programmatic config)"""
    logging.info("=== Example 4: Explicit config ===")
    
    try:
        # Pass config programmatically
        config = {
            "mcpServers": {
                "viaNexus": {
                    "server_url": "http://localhost",
                    "server_port": 8080,
                    "software_statement": "test_statement"
                }
            }
        }
        
        client = AnthropicClient(config=config)
        await client.connect_and_run()
    except Exception as e:
        logging.error(f"Explicit config example failed: {e}")

async def example_different_llm():
    """Example 5: Using a different LLM client"""
    logging.info("=== Example 5: Different LLM client ===")
    
    try:
        # Use OpenAI client instead
        client = OpenAiClient()  # Also auto-loads config!
        await client.connect_and_run()
    except Exception as e:
        logging.error(f"Different LLM example failed: {e}")

async def main():
    """Run all examples"""
    logging.basicConfig(level=logging.INFO)
    
    # Uncomment the example you want to run
    # await example_auto_config()
    # await example_custom_environment()
    # await example_custom_config_path()
    # await example_explicit_config()
    # await example_different_llm()
    
    logging.info("No examples selected. Uncomment one in main() to run it.")

if __name__ == "__main__":
    asyncio.run(main())
