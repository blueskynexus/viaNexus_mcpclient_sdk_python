from openai import AsyncOpenAI
import asyncio, json, logging
from typing import Any, Dict, List, Tuple
from vianexus_agent_sdk.clients.setup.enhanced_mcp_client import EnhancedMCPClient

class OpenAiClient(EnhancedMCPClient):
    def __init__(self, config):
        super().__init__(config)
        self.openai = AsyncOpenAI(api_key=config.get("llm_api_key"))
        # Pick a modern model you actually provision; keep configurable
        self.model = config.get("llm_model", "gpt-4o-mini")

    @staticmethod
    def _map_tool(t):
        # Pass through MCP schema or default to an object
        schema = getattr(t, "inputSchema", None) or {"type": "object", "properties": {}}

        def has_types(obj_props):
            return all(isinstance(v, dict) and "type" in v for v in obj_props.values())

        is_object = schema.get("type") == "object"
        props = schema.get("properties", {}) if isinstance(schema.get("properties"), dict) else {}
        addl = schema.get("additionalProperties", None)
        can_be_strict = is_object and addl is False and has_types(props)

        fn = {
            "name": t.name,
            "description": t.description or "",
            "parameters": schema,
        }
        fn["description"] += ("\n\nminimum: 0") 
        if can_be_strict:
            fn["strict"] = True  # only when schema already satisfies strict requirements

        return {"type": "function", "function": fn}

    async def _list_tools_for_openai(self) -> List[Dict[str, Any]]:
        tool_list = await self.session.list_tools()
        return [self._map_tool(t) for t in (tool_list.tools or [])]
 
    async def _stream_assistant(self, messages, tools, timeout=60):
        text_out = []
        tool_calls = {}  # id -> {"id", "type":"function", "function":{"name","arguments"}}

        async with self.openai.chat.completions.stream(
            model=self.model, messages=messages, tools=tools or None, timeout=timeout
        ) as stream:
            async for chunk in stream:
                c = chunk.choices[0]
                d = c.delta

                if d.content:
                    text_out.append(d.content)

                if d.tool_calls:
                    for tc in d.tool_calls:
                        call_id = tc.id or f"call_{len(tool_calls)}"
                        item = tool_calls.setdefault(
                            call_id,
                            {"id": call_id, "type": "function",
                            "function": {"name": "", "arguments": ""}}
                        )
                        if tc.function and tc.function.name:
                            item["function"]["name"] = tc.function.name
                        if tc.function and tc.function.arguments:
                            item["function"]["arguments"] += tc.function.arguments

        assistant_msg = {
            "role": "assistant",
            "content": "".join(text_out),
        }
        if tool_calls:
            assistant_msg["tool_calls"] = list(tool_calls.values())

        return assistant_msg["content"], tool_calls, assistant_msg

    async def process_query(self, query: str) -> str:
        if not self.session:
            return "Error: MCP session not initialized."

        tools = await self._list_tools_for_openai()
        messages: List[Dict[str, Any]] = [{"role": "user", "content": query}]
        printed_any = False

        for _ in range(6):  # safety cap on tool iterations
            text, tool_calls, assistant_msg = await self._stream_assistant(messages, tools)
            messages.append(assistant_msg)

            if not tool_calls:
                if text:
                    print(text)
                    printed_any = True
                return "" if printed_any else text

            # Execute all tool calls
            tool_results_msgs: List[Dict[str, Any]] = []
            for call in tool_calls.values():
                name = call["function"]["name"]
                arg_str = call["function"]["arguments"] or "{}"
                try:
                    args = json.loads(arg_str) if arg_str.strip() else {}
                except json.JSONDecodeError:
                    args = {"_raw": arg_str}
                try:
                    result = await self.session.call_tool(name, args)
                    payload = getattr(result, "content", result)
                    if not isinstance(payload, str):
                        payload = json.dumps(payload, ensure_ascii=False)
                except Exception as e:
                    logging.error("Tool %s failed: %s", name, e)
                    payload = f"Error calling tool '{name}': {e}"

                tool_results_msgs.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "name": name,
                    "content": payload[:100_000],
                })

            # Provide all tool results at once and loop
            messages.extend(tool_results_msgs)

        return "Error: tool-call loop exceeded max iterations."
