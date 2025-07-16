# viaNexus MCP Client SDK for Python

The viaNexus MCP Client SDK for Python provides a convenient way to interact with the viaNexus Multi-modal Conversation Platform (MCP). This SDK allows you to build powerful conversational AI applications with Gemini models, leveraging the capabilities of the MCP platform.

## Installation

To install the SDK, you can use pip:

```bash
pip install vianexus-mcp-client-sdk
```

**Note:** This SDK depends on other packages like `google-ads-sdk` and `mcp-client`. Make sure these are correctly installed in your environment.

## Usage

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
    # This will handle the OAuth 2.0 flow to authenticate with the MCP server.
    # It will start a local server to handle the redirect callback.
    oauth_provider_manager = ViaNexusOAuthProvider(
        name="my-app",
        server_url="https://mcp.vianexus.com", # Replace with your server URL
        server_port="443", # Replace with your server port
        user_credentials="path/to/your/credentials.json" # Replace with path to your credentials
    )
    oauth_provider = await oauth_provider_manager.initialize()

    # 2. Create connection parameters from the OAuth provider
    # We assume StreamableHTTPConnectionParams can be initialized with the oauth_provider object.
    # If this is not the case, you might need to adapt this part based on the documentation
    # of the underlying libraries.
    connection_params = StreamableHTTPConnectionParams(oauth_provider)

    # 3. Create a toolset
    mcp_toolset = GeminiMCPToolset(connection_params=connection_params)

    # 4. Create a Gemini agent
    agent = GeminiLLMAgent(
        model="gemini-pro",
        name="my-gemini-agent",
        description="A simple Gemini agent.",
        instruction="You are a helpful assistant.",
        input_schema=None,  # Define your input schema if needed
        tools=[mcp_toolset],
        output_key=None
    )

    # 5. Create a runner and execute the agent
    runner = GeminiRunner(agent=agent, name="my-runner", session_id="my-session")
    await runner.initialize()
    response = await runner.run_async("Hello, who are you?")
    print(f"Agent response: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Contributing

We welcome contributions to the viaNexus MCP Client SDK for Python. If you would like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with a clear and descriptive message.
4.  Push your changes to your fork.
5.  Create a pull request to the main repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details. 
