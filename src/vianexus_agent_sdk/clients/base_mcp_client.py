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
            logging.info(f"Connected to server with tools: {[tool.name for tool in tools]}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        logging.info("\nMCP Client Started!")
        logging.info("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                logging.info("\n" + response)

            except Exception as e:
                logging.error(f"\nError: {str(e)}")
    
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
