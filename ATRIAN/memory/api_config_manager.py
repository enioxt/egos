#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API Configuration Manager for ATRiAN Memory System

This module provides configuration management for the ATRiAN memory system's API connections.
It loads settings from the api_config.yaml file and provides an interface for accessing
environment-specific configurations and feature flags.

MQP Alignment:
- Systemic Cartography (SC): Providing a centralized configuration system
- Sacred Privacy (SP): Managing sensitive API credentials
- Evolutionary Preservation (EP): Supporting multiple environments and versioning

Version: 0.1.0
Created: 2025-05-27
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import os
import yaml
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "api_config.yaml")
ENV_VAR_PREFIX = "ATRIAN_"
ENV_VAR_ENV = f"{ENV_VAR_PREFIX}ENVIRONMENT"


class ATRiANConfigManager:
    """
    Configuration manager for ATRiAN memory system API connections.
    
    This class provides a centralized way to manage API configurations across
    different environments (development, testing, staging, production).
    """
    
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        """
        Initialize the configuration manager.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.current_environment: str = ""
        self._load_config()
        
        # Display EGOS banner
        self._print_banner()
    
    def _print_banner(self):
        """Print ATRiAN Configuration Manager banner."""
        banner = """
        ╔═══════════════════════════════════════════════╗
        ║                                               ║
        ║      ATRiAN API Configuration Manager         ║
        ║                                               ║
        ╚═══════════════════════════════════════════════╝
        """
        logger.info(banner)
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        try:
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
                logger.info(f"Loaded configuration from {self.config_path}")
            
            # Determine environment
            env = os.environ.get(ENV_VAR_ENV, self.config.get("default_environment", "development"))
            self.current_environment = env
            logger.info(f"Using environment: {self.current_environment}")
            
            # Override with environment variables
            self._override_with_env_vars()
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError:
            logger.error(f"Error parsing configuration file: {self.config_path}")
            raise
    
    def _override_with_env_vars(self) -> None:
        """Override configuration with environment variables."""
        env_config = self.get_environment_config()
        if not env_config:
            return
        
        for key in env_config:
            env_var = f"{ENV_VAR_PREFIX}{self.current_environment.upper()}_{key.upper()}"
            if env_var in os.environ:
                env_config[key] = os.environ[env_var]
                logger.debug(f"Overriding {key} with environment variable {env_var}")
    
    def get_environment_config(self) -> Dict[str, Any]:
        """
        Get configuration for the current environment.
        
        Returns:
            Dict[str, Any]: Environment configuration
        """
        try:
            return self.config.get("environments", {}).get(self.current_environment, {})
        except (AttributeError, KeyError):
            logger.error(f"Environment {self.current_environment} not found in configuration")
            return {}
    
    def get_feature_flag(self, feature_name: str) -> Any:
        """
        Get a feature flag value.
        
        Args:
            feature_name (str): Name of the feature flag
            
        Returns:
            Any: Feature flag value or None if not found
        """
        try:
            return self.config.get("features", {}).get(feature_name)
        except (AttributeError, KeyError):
            logger.warning(f"Feature flag {feature_name} not found in configuration")
            return None
    
    def get_api_base_url(self) -> str:
        """
        Get the base URL for API requests.
        
        Returns:
            str: API base URL
        """
        return self.get_environment_config().get("api_base_url", "http://localhost:8000/api/v1/atrian")
    
    def get_api_key(self) -> Optional[str]:
        """
        Get the API key for authentication.
        
        Returns:
            Optional[str]: API key or None if not configured
        """
        return self.get_environment_config().get("api_key")
    
    def get_timeout(self) -> int:
        """
        Get the request timeout in seconds.
        
        Returns:
            int: Timeout in seconds
        """
        return self.get_environment_config().get("timeout", 5)
    
    def get_retry_settings(self) -> Dict[str, int]:
        """
        Get retry settings.
        
        Returns:
            Dict[str, int]: Retry count and delay settings
        """
        env_config = self.get_environment_config()
        return {
            "count": env_config.get("retry_count", 3),
            "delay": env_config.get("retry_delay", 1)
        }
    
    def get_namespace(self) -> str:
        """
        Get the namespace for data storage.
        
        Returns:
            str: Namespace
        """
        return self.get_environment_config().get("namespace", "atrian")
    
    def list_environments(self) -> List[str]:
        """
        List all available environments.
        
        Returns:
            List[str]: List of environment names
        """
        try:
            return list(self.config.get("environments", {}).keys())
        except (AttributeError, KeyError):
            logger.error("Failed to list environments")
            return []
    
    def switch_environment(self, environment: str) -> bool:
        """
        Switch to a different environment.
        
        Args:
            environment (str): Environment name
            
        Returns:
            bool: True if switch was successful, False otherwise
        """
        if environment in self.list_environments():
            self.current_environment = environment
            logger.info(f"Switched to environment: {environment}")
            return True
        else:
            logger.error(f"Environment {environment} not found in configuration")
            return False


# Singleton instance for global access
_config_manager: Optional[ATRiANConfigManager] = None


def get_config_manager(config_path: str = DEFAULT_CONFIG_PATH) -> ATRiANConfigManager:
    """
    Get the global configuration manager instance.
    
    Args:
        config_path (str, optional): Path to configuration file. Defaults to DEFAULT_CONFIG_PATH.
        
    Returns:
        ATRiANConfigManager: Configuration manager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ATRiANConfigManager(config_path)
    return _config_manager


if __name__ == "__main__":
    # Script execution entry point for testing or command-line usage
    config_manager = get_config_manager()
    
    # Print current configuration
    print(f"Current environment: {config_manager.current_environment}")
    print(f"API Base URL: {config_manager.get_api_base_url()}")
    print(f"API Key present: {'Yes' if config_manager.get_api_key() else 'No'}")
    print(f"Timeout: {config_manager.get_timeout()} seconds")
    print(f"Retry settings: {config_manager.get_retry_settings()}")
    print(f"Available environments: {config_manager.list_environments()}")