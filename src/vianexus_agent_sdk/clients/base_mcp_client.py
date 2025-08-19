import logging
from contextlib import AsyncExitStack
from mcp import ClientSession
from abc import ABC, abstractmethod

class BaseMCPClient(ABC):
    """
    Base class for MCP clients that provides common functionality
    for connecting to MCP servers and running chat loops.
    """
    
    def __init__(self, readstream, writestream):
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.readstream = readstream
        self.writestream = writestream
    
    async def connect_to_server(self):
        """Connect to the MCP server"""
        try:
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.readstream, self.writestream))
            await self.session.initialize()
            
            # List available tools
            response = await self.session.list_tools()
            tools = response.tools
            logging.debug(f"Connected to server with tools: {[tool.name for tool in tools]}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        # Use print() for user-facing messages
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        print("=" * 50)

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    print("\nGoodbye!")
                    break

                if not query:
                    print("Please enter a query.")
                    continue

                print("\nProcessing...")
                response = await self.process_query(query)
                
                # Use print() for the AI response
                print("\n" + "=" * 50)
                print("Response:")
                print(response)
                print("=" * 50)

            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Goodbye!")
                break
            except Exception as e:
                # Use print() for user-facing errors, logging for system errors
                print(f"\nError: {str(e)}")
                logging.error(f"Chat loop error: {e}")
    
    @abstractmethod
    async def process_query(self, query: str) -> str:
        """
        Process a query using the specific AI model and available tools.
        Must be implemented by subclasses.
        """
        pass
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
