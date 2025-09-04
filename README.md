# viaNexus AI Agent SDK for Python

The viaNexus AI Agent SDK for Python provides a convenient way to create a financial data agent with access to reliable financial data through viaNexus.
This SDK allows you to build a powerful financial Agent or digital employee/assitant that will have access to the viaNexus Data Platform financial dataset catalog.

## Installation

To install the SDK, you can use uv:

```bash
    uv add git+https://github.com/blueskynexus/viaNexus-agent-sdk-python --tag v0.1.17-pre
```
### Dependencies
- None required
- vianexus_agent_sdk will pull in all of the required dependencies.
- **Note:** _Do not install the google-adk module from google, use the one provided by the vianexus_agent_sdk it has been patched to follow OAuth authentication protocol in the HTTP transport_

## Usage
## LLM Support

Currently, the viaNexus AI Agent SDK for Python supports Google's Gemini and Anthropic family of models. As the SDK matures, we plan to extend support to other Large Language Models (LLMs) to provide a wider range of options for your conversational AI applications.


### OAuth
**Note:** OAuth is handled by the viaNexus_agent_sdk in the HTTP transport, you do not need to setup any authentication or authorization mechanisms
### Create a configuration file `config.yaml`
```yaml
development:
  LLM_API_KEY: "<LLM API Key>" # Supports both GEMINI and Anthropic (Claude) API keys
  LLM_MODEL: "<Model Name>" # Examples: gemini-2.5-flash, claude-3-5-sonnet-20241022
  LOG_LEVEL: "<LOGGING LEVEL>"
  max_tokens: 1000 # Optional: Maximum tokens for responses
  user_id: "<UUID for the Agent Session>"
  app_name: "viaNexus_Agent"
  agentServers:
    viaNexus:
      server_url: "<viaNexus Agent Server HTTP URL>"
      server_port: <viaNexus Agent Port>
      software_statement: "<SOFTWARE STATEMENT>"
```
**Note:** Generate a software statement from the viaNexus api endpoint `v1/agents/register`

### Anthropic Client Setup

The `AnthropicClient` provides two usage modes for different integration scenarios:

1. **Interactive REPL Mode**: For interactive chat sessions
2. **Single Question Mode**: For programmatic integration where you need string responses

#### Configuration

First, create a configuration dictionary with the required parameters:

```python
config = {
    "llm_api_key": "your-anthropic-api-key",
    "llm_model": "claude-3-5-sonnet-20241022",  # or your preferred Claude model
    "max_tokens": 1000,
    "max_history_length": 50,
    "server": "your-vianexus-server-url",
    "port": 443,
    "software_statement": "your-software-statement-jwt"
}
```

#### Mode 1: Interactive REPL Chat

Use this mode for interactive chat sessions where responses are streamed to the console:

```python
import asyncio
from vianexus_agent_sdk.clients.anthropic_client import AnthropicClient

async def interactive_mode():
    """Run the client in interactive REPL mode."""
    config = {
        "llm_api_key": "your-anthropic-api-key",
        "llm_model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1000,
        "server": "your-vianexus-server-url",
        "port": 443,
        "software_statement": "your-software-statement-jwt"
    }
    
    try:
        client = AnthropicClient(config)
        await client.run()  # Starts interactive chat loop
    except Exception as e:
        print(f"Connection setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(interactive_mode())
```

#### Mode 2: Single Question Integration

Use this mode when you need to integrate the client into your application and get programmatic responses:

```python
import asyncio
from vianexus_agent_sdk.clients.anthropic_client import AnthropicClient

async def single_question_mode():
    """Use the client for single questions with string responses."""
    config = {
        "llm_api_key": "your-anthropic-api-key", 
        "llm_model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1000,
        "server": "your-vianexus-server-url",
        "port": 443,
        "software_statement": "your-software-statement-jwt"
    }
    
    client = AnthropicClient(config)
    
    try:
        # Setup connection
        if not await client.setup_connection():
            print("Failed to setup connection")
            return
            
        # Establish MCP session
        async with client.connection_manager.connection_context() as (readstream, writestream, get_session_id):
            client.readstream = readstream
            client.writestream = writestream
            
            if not await client.connect_to_server():
                print("Failed to connect to MCP server")
                return
                
            # Now you can ask single questions
            response = await client.ask_single_question("What is the current price of AAPL?")
            print(f"Response: {response}")
            
            response = await client.ask_single_question("Show me the 52-week high and low for TSLA")
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(single_question_mode())
```

#### Configuration from YAML File

You can also load configuration from a YAML file:

```python
import yaml
import asyncio
from vianexus_agent_sdk.clients.anthropic_client import AnthropicClient

async def main():
    # Load config from YAML
    with open('config.yaml', 'r') as file:
        full_config = yaml.safe_load(file)
        env_config = full_config.get('development', {})
    
    # Prepare client config
    client_config = {
        "llm_api_key": env_config.get("LLM_API_KEY"),
        "llm_model": env_config.get("LLM_MODEL", "claude-3-5-sonnet-20241022"),
        "max_tokens": env_config.get("MAX_TOKENS", 1000),
        "server": env_config["agentServers"]["viaNexus"]["server_url"],
        "port": env_config["agentServers"]["viaNexus"]["server_port"],
        "software_statement": env_config["agentServers"]["viaNexus"]["software_statement"]
    }
    
    client = AnthropicClient(client_config)
    
    # Use either mode
    await client.run()  # Interactive mode
    # OR
    # response = await client.ask_single_question("Your question")  # Single question mode

if __name__ == "__main__":
    asyncio.run(main())
```

#### Integration in Your Application

Here's how to integrate the client into a web application or service:

```python
from fastapi import FastAPI
from vianexus_agent_sdk.clients.anthropic_client import AnthropicClient
import asyncio

app = FastAPI()
client = None

@app.on_event("startup")
async def startup_event():
    global client
    config = {
        "llm_api_key": "your-anthropic-api-key",
        "llm_model": "claude-3-5-sonnet-20241022",
        "server": "your-vianexus-server-url", 
        "port": 443,
        "software_statement": "your-software-statement-jwt"
    }
    
    client = AnthropicClient(config)
    await client.setup_connection()

@app.post("/ask")
async def ask_question(question: str):
    """API endpoint to ask financial questions."""
    try:
        async with client.connection_manager.connection_context() as (readstream, writestream, get_session_id):
            client.readstream = readstream
            client.writestream = writestream
            
            if not await client.connect_to_server():
                return {"error": "Failed to connect to MCP server"}
                
            response = await client.ask_single_question(question)
            return {"response": response}
            
    except Exception as e:
        return {"error": str(e)}

@app.on_event("shutdown") 
async def shutdown_event():
    if client:
        await client.cleanup()
```

#### Key Differences Between Modes

| Feature | Interactive REPL Mode | Single Question Mode |
|---------|----------------------|---------------------|
| Method | `client.run()` | `client.ask_single_question(question)` |
| Output | Streams to console | Returns string |
| Use Case | Interactive chat | Programmatic integration |
| Message History | Persistent across questions | Isolated per question |
| Streaming | Yes | No |

The transport layer is established in our StreamableHTTPSetup class
The connection and data layer is managed by the session, and is initialized in our BaseMCPClient class

### Gemini Example Setup
Here's a basic example of how to use the SDK to create a Gemini agent and run it:

```python
import asyncio
from vianexus_agent_sdk.gemini.agents.llm_agent import GeminiLLMAgent
from vianexus_agent_sdk.gemini.runners.runner import GeminiRunner
from vianexus_agent_sdk.gemini.tools.agent_toolset import GeminiAgentToolset
from vianexus_agent_sdk.providers.oauth import ViaNexusOAuthProvider
# The following import is a patched fork of the adk-python which provides support for OAuth protocol through HTTP transport
from google.adk.tools.agent_tool.agent_session_manager import StreamableHTTPConnectionParams

async def main():
    # Before anything set the GEMINI API KEY as an Environment variable
    os.environ["GEMINI_API_KEY"] = config["LLM_API_KEY"]

    # 1. Set up the OAuth provider and authenticate
    # This will handle the OAuth 2.0 flow to authenticate with the viaNexus Agent server.
    # It will start a local server to handle the redirect callback.
    oauth_provider_manager = ViaNexusOAuthProvider(
        server_url="URL for the viaNexus Agent Server>", # Discovery of Auth server, the server providing /.well-known/oauth-protected-resource
        server_port="<Port for the viaNexus Agent Server>", # Replace with viaNexus Agent server port
        software_statement="JWT software statement"
    )
    # Intialize the OAuth client and starts the Callback server for client side of OAuth2.0/2.1
    oauth_provider = await oauth_provider_manager.initialize()

    # 2. Create connection parameters from the.oauth_provider
    connection_params = StreamableHTTPConnectionParams(
        # Remove trailing forward slash
            url=f"{server_url}:{server_port}/agent",
            auth=oauth_provider,
    )

    # 3. Create a toolset
    agent_toolset = GeminiAgentToolset(connection_params=connection_params)

    # 4. Create a Gemini agent
    agent = GeminiLLMAgent(
        model="<GEMINI model i.e. gemini-2.5-flash>",
        tools=[agent_toolset],
    )

    # 5. Create a runner and execute the agent
    runner = GeminiRunner(agent=agent, app_name="my-runner", user_id="UUID for the session", session_id="my-session")
    await runner.initialize()

     while True:
        try:
            query = input("Enter a query: ")
            logging.debug(f"Query: {query}")
            if query == "exit":
                break
            if not query:
                continue
            async for event in runner.run_async(query):
                logging.info(f"Agent: {event}")
        except KeyboardInterrupt:
            logging.warning("Exiting...")
            break
        except Exception as e:
            logging.warning(f"Error: {e}")
            continue

if __name__ == "__main__":
    asyncio.run(main())

```

## Contributing

We welcome contributions to the viaNexus AI Agent SDK for Python. If you would like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with a clear and descriptive message.
4.  Push your changes to your fork.
5.  Create a pull request to the main repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
