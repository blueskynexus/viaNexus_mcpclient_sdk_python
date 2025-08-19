from vianexus_agent_sdk.clients.base_mcp_client import BaseMCPClient
from vianexus_agent_sdk.clients.streamable_http import StreamableHttpSetup
import logging

class EnhancedMCPClient(BaseMCPClient):
    """
    Enhanced MCP client that automatically handles connection setup and authentication.
    Subclasses only need to implement process_query().
    """
    
    def __init__(self, config):
        self.config = config
        self.connection_manager = None
        self.auth_layer = None
        # Initialize with None streams, will be set during connection
        super().__init__(None, None)
    
    async def setup_connection(self):
        """Set up the connection and authentication layer"""
        try:
            # Create connection manager and establish auth layer
            self.connection_manager = StreamableHttpSetup(self.config)
            self.auth_layer = await self.connection_manager.create_auth_layer()
            return True
        except Exception as e:
            logging.error(f"Failed to setup connection: {e}")
            return False
    
    async def connect_and_run(self):
        """Complete setup, connect, and run the chat loop"""
        if not await self.setup_connection():
            return False
            
        try:
            # Get the connection context and establish transport
            async with self.connection_manager.get_connection_context() as (readstream, writestream, get_session_id):
                logging.debug("HTTP transport established")
                
                # Update our streams
                self.readstream = readstream
                self.writestream = writestream
                
                if await self.connect_to_server():
                    await self.chat_loop()
                else:
                    logging.error("Failed to initialize MCP session")
                    return False
                    
        except Exception as e:
            logging.error(f"Connection setup failed: {e}")
            return False
        
        return True
    
    async def cleanup(self):
        """Clean up resources"""
        await super().cleanup()
        if self.connection_manager:
            # Additional cleanup if needed
            pass
