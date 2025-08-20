from anthropic import AsyncAnthropic
import logging
from vianexus_agent_sdk.clients.setup.enhanced_mcp_client import EnhancedMCPClient


class AnthropicClient(EnhancedMCPClient):
    def __init__(self, config):
        super().__init__(config)
        self.anthropic = AsyncAnthropic(api_key=config.get("llm_api_key"))
        self.model = config.get("llm_model", "claude-3-5-sonnet-20241022")
        self.max_tokens = config.get("max_tokens", 1000)

    async def process_query(self, query: str) -> str:
        if not self.session:
            return "Error: MCP session not initialized."

        try:
            tool_list = await self.session.list_tools()
            tools = [{
                "name": t.name,
                "description": t.description or "",
                "input_schema": t.inputSchema,  # MCP -> Anthropic shape
            } for t in (tool_list.tools or [])]
        except Exception as e:
            logging.error("Error listing tools: %s", e)
            tools = []

        messages = [{"role": "user", "content": query}]
        final_text_parts = []

        while True:
            resp = await self.anthropic.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=messages,
                tools=tools if tools else None,
                timeout=30,
            )

            # Emit any assistant text
            saw_tool_use = False
            assistant_blocks = []
            for block in resp.content:
                if block.type == "text":
                    final_text_parts.append(block.text)
                    assistant_blocks.append(block)
                elif block.type == "tool_use":
                    saw_tool_use = True
                    assistant_blocks.append(block)

                    tool_name = block.name
                    tool_args = block.input if isinstance(block.input, dict) else {}
                    try:
                        result = await self.session.call_tool(tool_name, tool_args)
                        # Coerce tool result to Anthropic content blocks
                        if isinstance(result.content, str):
                            tool_result_content = [{"type": "text", "text": result.content}]
                        else:
                            # Extract text from TextContent or other MCP content types
                            if hasattr(result.content, 'text'):
                                text_content = result.content.text
                            elif hasattr(result.content, 'content'):
                                text_content = result.content.content
                            else:
                                text_content = str(result.content)
                            tool_result_content = [{"type": "text", "text": text_content}]
                    except Exception as e:
                        logging.error("Tool call failed: %s", e)
                        tool_result_content = [{"type": "text", "text": f"Error: {e}"}]

                    # Continue the turn: assistant announces tool_use, user supplies tool_result
                    messages.append({"role": "assistant", "content": assistant_blocks})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_result_content,
                        }],
                    })
                    break  # send next Anthropic call with new messages

            if not saw_tool_use:
                # No more tool calls; conversation turn is done
                break

        return "\n".join([t for t in final_text_parts if t])
