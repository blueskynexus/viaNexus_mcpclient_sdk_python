from typing import Any
from google.adk.agents.llm_agent import LlmAgent
from pydantic import BaseModel
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

class GeminiLLMAgent(LlmAgent):
    model: str
    tools: list[MCPToolset]
    
    def __init__(self, model: str, tools: list[MCPToolset]):
        super().__init__(
            name="ViaNexus_Agent",
            model=model,
            description="An agent for the viaNexus financial data platform.",
            instruction="You are a helpful financial data assistant, an agent for the viaNexus financial data platform.",
            input_schema=None,
            tools=tools,
            output_key=None
        )