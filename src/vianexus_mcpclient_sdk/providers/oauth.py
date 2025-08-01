import asyncio
from typing import Any
import requests
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken
from vianexus_mcpclient_sdk.servers.callback.callback_server import CallbackServer
from mcp import ClientSession
from urllib.parse import urljoin
import httpx

def patch_oauth_provider_with_software_statement(provider: OAuthClientProvider, software_statement: str):
    """Monkey patch the OAuth provider to include software statement in registration."""
    
    original_register_client = provider._register_client
    
    async def patched_register_client():
        """Build registration request with software statement."""
        if provider.context.client_info:
            return None

        if provider.context.oauth_metadata and provider.context.oauth_metadata.registration_endpoint:
            registration_url = str(provider.context.oauth_metadata.registration_endpoint)
        else:
            auth_base_url = provider.context.get_authorization_base_url(provider.context.server_url)
            registration_url = urljoin(auth_base_url, "/register")

        registration_data = provider.context.client_metadata.model_dump(by_alias=True, mode="json", exclude_none=True)
        
        # Add software statement
        registration_data["software_statement"] = software_statement

        return httpx.Request(
            "POST", registration_url, json=registration_data, headers={"Content-Type": "application/json"}
        )
    
    provider._register_client = patched_register_client



class ViaNexusOAuthProvider:
    """Manages MCP server connections and tool execution."""

    def __init__(self, server_url: str, server_port: str, software_statement: str) -> None:
        self.name: str = "ViaNexus_OAuthProvider"
        self.server_url: str = server_url
        self.server_port: str = server_port if server_port else "443"
        self.software_statement: str = software_statement

    async def initialize(self) -> tuple[ClientSession, str]:
        """Initialize the server connection."""
        try:
            callback_server = CallbackServer(port=3030)
            callback_server.start()

            async def callback_handler() -> tuple[str, str | None]:
                """Wait for OAuth callback and return auth code and state."""
                try:
                    auth_code = callback_server.wait_for_callback(timeout=300)
                    return auth_code, callback_server.get_state()
                except Exception as e:
                    raise e

            client_metadata_dict = {
                "client_name": "ViaNexus Auth Client",
                "redirect_uris": ["http://localhost:3030/callback"],
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
                "token_endpoint_auth_method": "client_secret_post",
            }

            async def _default_redirect_handler(authorization_url: str) -> None:
                """Default redirect handler that opens the URL in a browser."""
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, requests.get, authorization_url)
                try:
                    response.raise_for_status()
                except Exception as e:
                    raise e

            oauth_provider = OAuthClientProvider(
                server_url=f"{self.server_url}:{self.server_port}",
                client_metadata=OAuthClientMetadata.model_validate(
                    client_metadata_dict
                ),
                storage=InMemoryTokenStorage(),
                redirect_handler=_default_redirect_handler,
                callback_handler=callback_handler,
            )
        except Exception as e:
            raise e

        patch_oauth_provider_with_software_statement(oauth_provider, self.software_statement)

        return oauth_provider


class InMemoryTokenStorage(TokenStorage):
    """Simple in-memory token storage implementation."""

    def __init__(self):
        self._tokens: OAuthToken | None = None
        self._client_info: OAuthClientInformationFull | None = None

    async def get_tokens(self) -> OAuthToken | None:
        return self._tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self._tokens = tokens

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        return self._client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self._client_info = client_info
    