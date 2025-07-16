from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import StreamableHTTPConnectionParams


class GeminiMCPToolset(MCPToolset):
    def __init__(self, connection_params: type[StreamableHTTPConnectionParams]):
        super().__init__(
            connection_params=connection_params
        )