# TODOS
- Move parent classes of clients to own subdirectory
- Drop configuration setup from sdk, env and config.yaml should be passed by the developer
- Figure out how to manage packages, llm dependencies shouldn't all download
- Gemini suppport

# viaNexus AI Agent SDK for Python

The viaNexus AI Agent SDK for Python provides a convenient way to create a financial data agent with access to reliable financial data through viaNexus.
This SDK allows you to build a powerful financial Agent or digital employee/assitant that will have access to the viaNexus Data Platform financial dataset catalog.

## Installation

To install the SDK, you can use uv:

```bash
    uv add git+https://github.com/blueskynexus/viaNexus-agent-sdk-python --tag v0.1.16-pre
```
### Dependencies
- None required
- vianexus_agent_sdk will pull in all of the required dependencies.
- **Note:** _Do not install the google-adk module from google, use the one provided by the vianexus_agent_sdk it has been patched to follow OAuth authentication protocol in the HTTP transport_

## Usage
### LLM Models
LLM selection or use is handled within the SDK, there is no need to integrate seperately, as LLM support expands, this list will grow accordingly.
- GEMINI: gemini-2.5-flash, gemini-2.5-pro

### OAuth
**Note:** OAuth is handled by the viaNexus_agent_sdk in the HTTP transport, you do not need to setup any authentication or authorization mechanisms
### Create a configuration file `config.yaml`
```yaml
development:
  LLM_API_KEY: "<LLM API Key>" # Currently only supports GEMINI
  LLM_MODEL: "<GEMINI Model Name>" # gemini-2.5-flash
  LOG_LEVEL: "<LOGGING LEVEL>"
  user_id: "<UUID for the Agent Session>"
  app_name: "viaNexus_Agent"
  agentServers:
    viaNexus:
      server_url: "<viaNexus Agent Server HTTP URL>"
      server_port: <viaNexus Agent Port>
      software_statement: "<SOFTWARE STATEMENT>"
```
**Note:** Generate a software statement from the viaNexus api endpoint `v1/agent/software-statement`

Here are examples of how to use the SDK to create an Anthropic agent and run it:

### Ultra-Simplified Approach (Recommended)

The SDK now provides automatic config loading! Just place your `config.yaml` in the project root:

```python
import asyncio
import logging
from dotenv import load_dotenv
from vianexus_agent_sdk.clients.anthropic_client import AnthropicClient

load_dotenv()  # load environment variables from .env

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
```

### Enhanced Client Approach

For more control over config loading:

```python
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
```

### Original Stepwise Approach

For maximum control over the connection process, you can still use the original approach:

```python
import asyncio
import logging
from dotenv import load_dotenv
from vianexus_agent_sdk.clients.streamable_http import StreamableHttpSetup
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
        # Create connection manager and establish auth layer
        connection_manager = StreamableHttpSetup(config)
        # Create the auth layer
        await connection_manager.create_auth_layer()
        # Get the connection context and establish transport
        async with connection_manager.get_connection_context() as (readstream, writestream, get_session_id):
            logging.debug("HTTP transport established")
            client = AnthropicClient(readstream, writestream)
            if await client.connect_to_server():
                await client.chat_loop()
            else:
                logging.error("Failed to initialize MCP session")
    
    except Exception as e:
        logging.error(f"Connection setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Config Options

The enhanced client supports various config loading options:

```python
# Auto-load from config.yaml (default)
client = AnthropicClient()

# Load from specific environment
client = AnthropicClient(env="production")

# Load from custom config file
client = AnthropicClient(config_path="my_config.yaml", env="staging")

# Pass config programmatically
config = {"mcpServers": {"viaNexus": {...}}}
client = AnthropicClient(config=config)
```

## LLM Support

Currently, the viaNexus AI Agent SDK for Python supports Google's Gemini, OpenAi, and Anthropic family of models. As the SDK matures, we plan to extend support to other Large Language Models (LLMs) to provide a wider range of options for your conversational AI applications.

## Contributing

We welcome contributions to the viaNexus AI Agent SDK for Python. If you would like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with a clear and descriptive message.
4.  Push your changes to your fork.
5.  Create a pull request to the main repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
