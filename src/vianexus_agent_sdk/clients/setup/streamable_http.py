from vianexus_agent_sdk.providers.oauth import ViaNexusOAuthProvider, ViaNexusOAuthClientProvider
from mcp.client.streamable_http import streamablehttp_client
from vianexus_agent_sdk.types.config import BaseConfig

class StreamableHttpSetup:
    """Manages MCP server authentication and connection setup"""
    
    def __init__(self, config:BaseConfig):
        self.server = config["server"]
        self.port = config["port"]
        self.software_statement = config["software_statement"]
        self.auth_layer = None
    
    async def create_auth_layer(self) -> ViaNexusOAuthClientProvider:
        """Create the auth flow pattern for mcp server connection"""
        oauth_provider_manager = ViaNexusOAuthProvider(
            server_url=self.server, # Discovery of Auth server, the server providing /.well-known/oauth-protected-resource
            server_port=self.port, # Replace with viaNexus MCP server port
            software_statement=self.software_statement, # Software statement goes here
        )
        # Intialize the OAuth client and starts the Callback server for client side of OAuth2.0/2.1
        self.auth_layer = await oauth_provider_manager.initialize()
        return self.auth_layer
    
    def get_connection_context(self):
        """Get the streamablehttp_client context manager for the established auth layer"""
        if not self.auth_layer:
            raise RuntimeError("Auth layer not created. Call create_auth_layer() first.")
        
        return streamablehttp_client(
            url=f"{self.server}:{self.port}/mcp",
            auth=self.auth_layer,
        )