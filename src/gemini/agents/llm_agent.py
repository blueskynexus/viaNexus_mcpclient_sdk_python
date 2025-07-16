from typing import Any
from google.adk.agents.llm_agent import LlmAgent
from pydantic import BaseModel
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

class GeminiLLMAgent(LlmAgent):
    def __init__(self, model: str, name: str, description: str, instruction: str, input_schema: BaseModel, tools: list[MCPToolset], output_key: str):
        self.name = name
        self.model = model
        self.description = description
        self.instruction = instruction
        self.input_schema = input_schema | None
        self.tools = tools
        self.output_key = output_key | None
        super().__init__(
            name=self.name,
            model=self.model,
            description=self.description,
            instruction=self.instruction,
            input_schema=self.input_schema,
            tools=self.tools,
            output_key=self.output_key
        )