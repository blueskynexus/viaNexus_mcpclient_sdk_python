# viaNexus MCP Client SDK for Python

The viaNexus MCP Client SDK for Python provides a convenient way to interact with the viaNexus Multi-modal Conversation Platform (MCP). This SDK allows you to build powerful conversational AI applications with Gemini models, leveraging the capabilities of the MCP platform.

## Installation

To install the SDK, you can use pip:

```bash
pip install vianexus-mcp-client-sdk
or
pip install https://github.com/blueskynexus/viaNexus_mcpclient_sdk_python/archive/refs/tags/v0.1.7-pre.tar.gz
```

## Usage
# Create a configuration file `config.yaml`
```yaml
development:
  LLM_API_KEY: "<LLM API Key>" # Currently only supports GEMINI
  LLM_MODEL: "<GEMINI Model Name>" # gemini-2.5-flash
  LOG_LEVEL: "<LOGGING LEVEL>"
  user_id: "<UUID for the Agent Session>"
  app_name: "viaNexus_Agent"
  mcpServers:
    viaNexus:
      user_credentials: "<Email Address to use for Authentication/Authorization>"
      server_url: "<viaNexus MCP Server HTTP URL>"
      server_port: <viaNexus MCP Port>
```

Here's a basic example of how to use the SDK to create a Gemini agent and run it:

```python
import asyncio
from gemini.agents.llm_agent import GeminiLLMAgent
from gemini.runners.runner import GeminiRunner
from gemini.tools.mcp_toolset import GeminiMCPToolset
from providers.oauth import ViaNexusOAuthProvider
# The following import is assumed for creating connection parameters.
from google.adk.tools.mcp_tool.mcp_toolset import StreamableHTTPConnectionParams 

async def main():
    # 1. Set up the OAuth provider and authenticate
    # This will handle the OAuth 2.0 flow to authenticate with the viaNexus MCP server.
    # It will start a local server to handle the redirect callback.
    oauth_provider_manager = ViaNexusOAuthProvider(
        server_url="URL for the viaNexus MCP Server>", # Discovery of Auth server, the server providing /.well-known/oauth-protected-resource
        server_port="443", # Replace with viaNexus MCP server port
        user_credentials="" # Replace with email address to use for Authorization and Authentication
    )
    # Intialize the OAuth client and starts the Callback server for client side of OAuth2.0/2.1
    oauth_provider = await oauth_provider_manager.initialize()

    # 2. Create connection parameters from the OAuth provider
    connection_params = StreamableHTTPConnectionParams(
            url=f"{server_url}:{server_port}/mcp/",
            auth=oauth_provider,
    )

    # 3. Create a toolset
    mcp_toolset = GeminiMCPToolset(connection_params=connection_params)

    # 4. Create a Gemini agent
    agent = GeminiLLMAgent(
        model="<GEMINI model i.e. gemini-2.5-flash>",
        tools=[mcp_toolset],
    )

    # 5. Create a runner and execute the agent
    runner = GeminiRunner(agent=agent, name="my-runner", session_id="my-session")
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

## LLM Support

Currently, the viaNexus MCP Client SDK for Python supports Google's Gemini family of models. As the SDK matures, we plan to extend support to other Large Language Models (LLMs) to provide a wider range of options for your conversational AI applications.

## Contributing

We welcome contributions to the viaNexus MCP Client SDK for Python. If you would like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with a clear and descriptive message.
4.  Push your changes to your fork.
5.  Create a pull request to the main repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details. 
