from vianexus_agent_sdk.clients.setup.base_mcp_client import BaseMCPClient
from vianexus_agent_sdk.clients.setup.streamable_http import StreamableHttpSetup
import logging
import yaml
import os
from dotenv import load_dotenv

class EnhancedMCPClient(BaseMCPClient):
    """
    Enhanced MCP client that automatically handles connection setup and authentication.
    Subclasses only need to implement process_query().
    """
    
    def __init__(self, config=None, config_path="config.yaml", env="development"):
        """
        Initialize the enhanced MCP client.
        
        Args:
            config: Configuration dictionary. If None, will attempt to auto-load from config_path
            config_path: Path to config file (relative to project root)
            env: Environment to load from config (default: "development")
        """
        # Load environment variables from .env file
        current_dir = os.getcwd()
        load_dotenv(os.path.join(current_dir, ".env"))
        
        if config is None:
            config = self.load_config(config_path, env)
        
        self.config = config
        self.connection_manager = None
        self.auth_layer = None
        # Initialize with None streams, will be set during connection
        super().__init__(None, None)
    
    @classmethod
    def load_config(cls, config_path="config.yaml", env="development"):
        """
        Automatically load configuration from a YAML file.
        
        Args:
            config_path: Path to config file (relative to project root)
            env: Environment to load from config
            
        Returns:
            Configuration dictionary for the specified environment
            
        Raises:
            FileNotFoundError: If config file is not found
            KeyError: If specified environment is not found in config
        """
        # Get the project root directory by looking for common indicators
        current_dir = os.getcwd()
        project_root = current_dir
        
        # Try to find the project root by looking for config.yaml
        while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
            if os.path.exists(os.path.join(current_dir, config_path)):
                project_root = current_dir
                break
            current_dir = os.path.dirname(current_dir)
        
        config_file_path = os.path.join(project_root, config_path)
        
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(
                f"Config file not found at {config_file_path}. "
                f"Please ensure {config_path} exists in your project root directory."
            )
        
        try:
            with open(config_file_path, "r") as f:
                full_yaml_config = yaml.safe_load(f)
            
            if env not in full_yaml_config:
                available_envs = list(full_yaml_config.keys())
                raise KeyError(
                    f"Environment '{env}' not found in config. "
                    f"Available environments: {available_envs}"
                )
            
            config = full_yaml_config[env]
            logging.debug(f"Loaded config from {config_file_path} for environment '{env}'")
            return config
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
    
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
    
    async def run(self):
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
