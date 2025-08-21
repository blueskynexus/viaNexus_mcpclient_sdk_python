from anthropic import AsyncAnthropic
import logging
import json
from vianexus_agent_sdk.mcp_client.enhanced_mcp_client import EnhancedMCPClient

class AnthropicClient(EnhancedMCPClient):
    def __init__(self, config):
        super().__init__(config)
        self.anthropic = AsyncAnthropic(api_key=config.get("llm_api_key"))
        self.model = config.get("llm_model", "claude-3-5-sonnet-20241022")
        self.max_tokens = config.get("max_tokens", 1000)

    async def process_query(self, query: str) -> str:
        if not self.session:
            return "Error: MCP session not initialized."

        # Discover MCP tools once per turn
        try:
            tool_list = await self.session.list_tools()
            tools = [{
                "name": t.name,
                "description": t.description or "",
                "input_schema": getattr(t, "inputSchema", {}) or {},
            } for t in (tool_list.tools or [])]
        except Exception as e:
            logging.error("Error listing tools: %s", e)
            tools = []

        messages = [{"role": "user", "content": query}]

        while True:
            # Stream assistant response
            async with self.anthropic.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=messages,
                tools=tools or None,
            ) as stream:
                # Live text stream
                async for event in stream:
                    if event.type == "content_block_delta" and getattr(event.delta, "type", "") == "text_delta":
                        print(event.delta.text, end="", flush=True)

                # Get the fully materialized assistant message (includes tool_use blocks)
                msg = await stream.get_final_message()

            # Collect tool_use blocks
            tool_uses = [b for b in msg.content if getattr(b, "type", None) == "tool_use"]
            # Add the assistant message we just streamed to the conversation
            messages.append({"role": "assistant", "content": msg.content})

            if not tool_uses:
                print()  # newline after final streamed text
                return ""  # already streamed to stdout

            # Execute tools and return results in a single user message
            result_blocks = []
            for tub in tool_uses:
                name = tub.name
                args = tub.input if isinstance(tub.input, dict) else {}
                try:
                    result = await self.session.call_tool(name, args)
                    # Normalize tool result to Anthropic content blocks
                    if isinstance(result, dict) and "content" in result:
                        payload = result["content"]
                    else:
                        payload = result
                    if isinstance(payload, (dict, list)):
                        text_payload = json.dumps(payload, ensure_ascii=False)
                    else:
                        text_payload = str(payload)
                    result_blocks.append({
                        "type": "tool_result",
                        "tool_use_id": tub.id,
                        "content": [{"type": "text", "text": text_payload}],
                    })
                except Exception as e:
                    logging.error("Tool '%s' failed: %s", name, e)
                    result_blocks.append({
                        "type": "tool_result",
                        "tool_use_id": tub.id,
                        "content": [{"type": "text", "text": f"Error: {e}"}],
                    })

            messages.append({"role": "user", "content": result_blocks})
