import logging
from anthropic import Anthropic
from vianexus_agent_sdk.clients.enhanced_mcp_client import EnhancedMCPClient

class AnthropicClient(EnhancedMCPClient):
    '''
    Anthropic-specific MCP client that uses Claude for processing queries.
    Inherits common MCP functionality from EnhancedMCPClient.
    '''
    def __init__(self, config):
        super().__init__(config)
        self.anthropic = Anthropic()
    
    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        if not self.session:
            return "Error: MCP session not initialized. Please check the connection."
        
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        try:
            response = await self.session.list_tools()
            available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]
        except Exception as e:
            logging.error(f"Error listing tools: {e}")
            available_tools = []

        if not available_tools:
            # If no tools available, just return a simple response
            try:
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages
                )
                return response.content[0].text
            except Exception as e:
                logging.error(f"Error calling Claude API: {e}")
                return f"Error: {str(e)}"

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                try:
                    result = await self.session.call_tool(tool_name, tool_args)
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                    final_text.append(f"Result: {result.content}")
                except Exception as e:
                    final_text.append(f"[Error calling tool {tool_name}: {str(e)}]")
                    result = type('obj', (object,), {'content': f"Error: {str(e)}"})()

                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)
