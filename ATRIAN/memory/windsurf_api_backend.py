#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - @references {C:\\EGOS\\ATRiAN\\memory\\windsurf_memory_adapter.py}
# - @references {C:\\EGOS\\ATRiAN\\atrian_windsurf_adapter.py}
# - @references {C:\\EGOS\\run_tools.py}
# --- 

import os
import sys
import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from urllib.parse import urljoin

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import backend interface
from memory.windsurf_memory_adapter import MemoryBackendInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("windsurf_api_backend")

class WindsurfAPIBackend(MemoryBackendInterface):
    """Memory backend implementation using the Windsurf API.
    
    This backend stores and retrieves data through the Windsurf API,
    enabling direct integration with Windsurf's memory system.
    
    Attributes:
        api_base_url (str): Base URL for the Windsurf API
        api_key (str): API key for authentication
        namespace (str): Namespace for ATRiAN memory data
        timeout (int): Timeout for API requests in seconds
        retry_count (int): Number of retries for failed requests
        retry_delay (int): Delay between retries in seconds
    """
    
    def __init__(self, api_base_url: str, api_key: str = None, namespace: str = "atrian",
                 timeout: int = 10, retry_count: int = 3, retry_delay: int = 1):
        """Initialize the Windsurf API backend.
        
        Args:
            api_base_url (str): Base URL for the Windsurf API
            api_key (str, optional): API key for authentication
            namespace (str, optional): Namespace for ATRiAN memory data
            timeout (int, optional): Timeout for API requests in seconds
            retry_count (int, optional): Number of retries for failed requests
            retry_delay (int, optional): Delay between retries in seconds
        """
        self.api_base_url = api_base_url.rstrip("/") + "/"
        self.api_key = api_key
        self.namespace = namespace
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        
        # Ensure API base URL ends with a slash
        if not self.api_base_url.endswith("/"):
            self.api_base_url += "/"
        
        # API endpoints
        self.endpoints = {
            "store": urljoin(self.api_base_url, "memory/store"),
            "retrieve": urljoin(self.api_base_url, "memory/retrieve"),
            "list": urljoin(self.api_base_url, "memory/list"),
            "delete": urljoin(self.api_base_url, "memory/delete"),
            "clear": urljoin(self.api_base_url, "memory/clear"),
            "health": urljoin(self.api_base_url, "health")
        }
        
        # Check API connection
        self._check_api_connection()
        
        logger.info(f"WindsurfAPIBackend initialized with base URL: {self.api_base_url}")
    
    def _check_api_connection(self) -> bool:
        """Check the connection to the Windsurf API.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            response = self._make_request("GET", self.endpoints["health"])
            if response.status_code == 200:
                logger.info("Successfully connected to Windsurf API")
                return True
            else:
                logger.warning(f"API health check failed with status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to Windsurf API: {str(e)}")
            return False
    
    def _make_request(self, method: str, url: str, data: Dict[str, Any] = None) -> requests.Response:
        """Make an API request with retry logic.
        
        Args:
            method (str): HTTP method (GET, POST, DELETE)
            url (str): API endpoint URL
            data (Dict[str, Any], optional): Request data
            
        Returns:
            requests.Response: API response
            
        Raises:
            requests.RequestException: If all retry attempts fail
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add API key if provided
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Retry logic
        for attempt in range(self.retry_count + 1):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, timeout=self.timeout)
                elif method.upper() == "POST":
                    response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, headers=headers, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check for successful response
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt < self.retry_count:
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.retry_count + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Request failed after {self.retry_count + 1} attempts: {str(e)}")
                    raise
    
    def _format_key(self, key: str) -> str:
        """Format a key for use with the API.
        
        Args:
            key (str): Original key
            
        Returns:
            str: Formatted key with namespace
        """
        return f"{self.namespace}:{key}"
    
    def store(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store a value with associated metadata.
        
        Args:
            key (str): The key to store the value under
            value (Any): The value to store
            metadata (Dict[str, Any], optional): Metadata to associate with the value
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare request data
            data = {
                "key": self._format_key(key),
                "value": value,
                "metadata": metadata or {}
            }
            
            # Add timestamp if not present
            if metadata and "timestamp" not in metadata:
                data["metadata"]["timestamp"] = datetime.now().isoformat()
            
            # Make API request
            response = self._make_request("POST", self.endpoints["store"], data)
            
            # Check response
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error storing {key}: {str(e)}")
            return False
    
    def retrieve(self, key: str) -> Tuple[Any, Dict[str, Any]]:
        """Retrieve a value and its metadata.
        
        Args:
            key (str): The key to retrieve
            
        Returns:
            Tuple[Any, Dict[str, Any]]: The value and its metadata
        """
        try:
            # Prepare request data
            data = {
                "key": self._format_key(key)
            }
            
            # Make API request
            response = self._make_request("POST", self.endpoints["retrieve"], data)
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                return result.get("value"), result.get("metadata", {})
            elif response.status_code == 404:
                return None, {}
            else:
                logger.warning(f"Unexpected status code retrieving {key}: {response.status_code}")
                return None, {}
        except Exception as e:
            logger.error(f"Error retrieving {key}: {str(e)}")
            return None, {}
    
    def list(self, prefix: str = "") -> List[str]:
        """List all keys with the given prefix.
        
        Args:
            prefix (str, optional): Prefix to filter keys by
            
        Returns:
            List[str]: List of keys matching the prefix
        """
        try:
            # Prepare request data
            data = {
                "prefix": self._format_key(prefix)
            }
            
            # Make API request
            response = self._make_request("POST", self.endpoints["list"], data)
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                keys = result.get("keys", [])
                
                # Remove namespace prefix from keys
                namespace_prefix = f"{self.namespace}:"
                return [
                    key[len(namespace_prefix):] for key in keys
                    if key.startswith(namespace_prefix)
                ]
            else:
                logger.warning(f"Unexpected status code listing keys: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing keys with prefix {prefix}: {str(e)}")
            return []
    
    def delete(self, key: str) -> bool:
        """Delete a value by key.
        
        Args:
            key (str): The key to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare request data
            data = {
                "key": self._format_key(key)
            }
            
            # Make API request
            response = self._make_request("DELETE", self.endpoints["delete"], data)
            
            # Check response
            return response.status_code in (200, 204)
        except Exception as e:
            logger.error(f"Error deleting {key}: {str(e)}")
            return False
    
    def clear(self, prefix: str = "") -> int:
        """Clear all values with the given prefix.
        
        Args:
            prefix (str, optional): Prefix to filter keys by
            
        Returns:
            int: Number of items cleared
        """
        try:
            # Prepare request data
            data = {
                "prefix": self._format_key(prefix)
            }
            
            # Make API request
            response = self._make_request("POST", self.endpoints["clear"], data)
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                return result.get("cleared_count", 0)
            else:
                logger.warning(f"Unexpected status code clearing keys: {response.status_code}")
                return 0
        except Exception as e:
            logger.error(f"Error clearing keys with prefix {prefix}: {str(e)}")
            return 0