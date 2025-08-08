from google.adk.tools.agent_tool.agent_toolset import AgentToolset
from google.adk.tools.agent_tool.agent_toolset import StreamableHTTPConnectionParams


class GeminiAgentToolset(AgentToolset):
    def __init__(self, connection_params: StreamableHTTPConnectionParams):
        super().__init__(
            connection_params=connection_params
        )