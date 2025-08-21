from google import genai

from vianexus_agent_sdk.mcp_client.enhanced_mcp_client import EnhancedMCPClient
from vianexus_agent_sdk.types.config import GeminiConfig

class GeminiClient(EnhancedMCPClient):
    """
    Gemini-specific MCP client that uses Gemini for processing queries.
    Inherits common MCP functionality from EnhancedMCPClient.
    """
    def __init__(self, config:GeminiConfig):
        '''
        Initialize the Gemini client.
        Args:
            config: Configuration dictionary, must contain llm_api_key, optional llm_model
        '''
        super().__init__(config)
        self.model = config.get("llm_model", "gemini-2.5-flash")
        self.client = genai.Client(api_key=config.get("llm_api_key"))
    
    def get_tool_list(self):
        tool_list = self.session.list_tools()
        formatted_tools = []
        for tool in tool_list.tools:
            formatted_tools.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": self.format_schema(tool.inputSchema),
            })
        return formatted_tools

    async def process_query(self, query: str) -> str:
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        while True:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=messages,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[self.session],                
                ),
            )
            return response.text