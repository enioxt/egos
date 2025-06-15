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

# - @references {C:\EGOS\ATRiAN\memory\demo_memory_integration.py}
# - @references {C:\EGOS\ATRiAN\memory\api_config.yaml}
# - @references {C:\EGOS\ATRiAN\memory\api_config_manager.py}
# ---

import os
import sys
import json
import time
import random
import logging
import argparse
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Optional, Tuple, Union

# Attempt to import the configuration manager
try:
    from .api_config_manager import get_config_manager, ATRiANConfigManager
except ImportError:
    # Fallback for direct execution or if not found in package structure
    from api_config_manager import get_config_manager, ATRiANConfigManager

# --- Constants ---
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000
LOG_FILE_NAME = "enhanced_mock_api_server.log"

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_NAME),
        logging.StreamHandler(sys.stdout)  # Also print to console
    ]
)
logger = logging.getLogger("EnhancedMockWindsurfAPI")

# --- In-memory storage for the mock API ---
# This simulates a simple database or persistence layer for the mock server.
storage: Dict[str, Dict[str, Any]] = {
    "memory_items": {},  # Stores: { "namespace/key": { "value": ..., "metadata": ... } }
    "access_log": [],    # Logs each request received by the server.
    "error_rules": []    # Rules for simulating errors, e.g., { "path_pattern": "/store", "method": "POST", "error_code": 500, "probability": 0.1 }
}

# --- EGOS Banner Function ---
def print_egos_banner(title: str):
    """Prints a standardized EGOS banner."""
    banner_width = 60
    padding = (banner_width - len(title) - 2) // 2
    banner = f"\n╔{'═' * (banner_width-2)}╗\n"
    banner += f"║ {'>' * padding} {title} {'<' * (banner_width - len(title) - 2 - padding -1)}║\n"
    banner += f"╚{'═' * (banner_width-2)}╝\n"
    logger.info(banner)

print_egos_banner("ATRiAN Enhanced Mock API Server Initializing")

# --- Global Configuration Manager Instance ---
# Initialize this early to make it available throughout the module.
try:
    config_manager: ATRiANConfigManager = get_config_manager()
    logger.info(f"Successfully initialized API Configuration Manager. Current environment: {config_manager.current_environment}")
except Exception as e:
    logger.error(f"Failed to initialize API Configuration Manager: {e}. Using default settings.")
    # Provide a fallback minimal config manager if initialization fails
    class MinimalConfigManager:
        current_environment = "fallback_dev"
        def get_api_base_url(self): return f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/api/v1/atrian"
        def get_feature_flag(self, flag_name): return False # Sensible defaults
        def get_namespace(self): return "atrian_fallback"
    config_manager = MinimalConfigManager()

logger.info("Enhanced Mock API Server Header Loaded.")

# End of Header Section

# --- Helper Functions for Mock API --- 
# These functions are intended to be used by the MockWindsurfAPIHandler class.

def parse_request_body(request_handler: BaseHTTPRequestHandler) -> Optional[Dict[str, Any]]:
    """Parses JSON request body."""
    try:
        content_length = int(request_handler.headers.get('Content-Length', 0))
        if content_length == 0:
            logger.debug("Request body is empty.")
            return None
        body_str = request_handler.rfile.read(content_length).decode('utf-8')
        logger.debug(f"Raw request body: {body_str}")
        return json.loads(body_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e} - Body: {body_str[:200]}") # Log first 200 chars
        return None
    except Exception as e:
        logger.error(f"Error parsing request body: {e}")
        return None

def send_response_util(request_handler: BaseHTTPRequestHandler, status_code: int, content_type: str, body: Union[str, bytes]):
    """Sends an HTTP response."""
    request_handler.send_response(status_code)
    request_handler.send_header('Content-type', content_type)
    request_handler.send_header('Access-Control-Allow-Origin', '*') # CORS for local dev
    request_handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, HEAD')
    request_handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    request_handler.end_headers()
    if isinstance(body, str):
        body = body.encode('utf-8')
    request_handler.wfile.write(body)
    logger.debug(f"Sent response: {status_code} - {content_type} - Body length: {len(body)}")

def send_json_response_util(request_handler: BaseHTTPRequestHandler, status_code: int, data: Dict[str, Any]):
    """Sends a JSON response."""
    send_response_util(request_handler, status_code, 'application/json', json.dumps(data))

def send_error_response_util(request_handler: BaseHTTPRequestHandler, status_code: int, message: str):
    """Sends a JSON error response."""
    send_json_response_util(request_handler, status_code, {"error": message, "status": status_code})

def log_request_util(request_handler: BaseHTTPRequestHandler, parsed_path: urlparse, query_params: Dict[str, List[str]]):
    """Logs details of an incoming request."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "method": request_handler.command,
        "path": parsed_path.path,
        "query_params": query_params,
        "client_address": request_handler.client_address[0],
        "headers": dict(request_handler.headers)
    }
    storage["access_log"].append(log_entry)
    logger.info(f"Request: {request_handler.command} {parsed_path.path} from {request_handler.client_address[0]}")
    if query_params:
        logger.debug(f"Query params: {query_params}")

def simulate_latency_util():
    """Simulates network latency based on configuration."""
    min_latency = config_manager.get_feature_flag("simulate_latency_min_ms") or 0
    max_latency = config_manager.get_feature_flag("simulate_latency_max_ms") or 0
    if max_latency > min_latency and max_latency > 0:
        latency_ms = random.uniform(min_latency, max_latency)
        sleep_seconds = latency_ms / 1000.0
        logger.info(f"Simulating latency: {latency_ms:.2f} ms")
        time.sleep(sleep_seconds)

def should_simulate_error_util(path: str, method: str) -> Optional[int]:
    """Determines if an error should be simulated for the current request."""
    if not (config_manager.get_feature_flag("enable_error_simulation") or False):
        return None
    
    # Example: specific error simulation rules (can be expanded via config_manager)
    # For now, a simple global error probability
    error_probability = config_manager.get_feature_flag("global_error_probability") or 0.0
    if random.random() < error_probability:
        simulated_error_code = config_manager.get_feature_flag("simulated_error_code") or 500
        logger.warning(f"Simulating a {simulated_error_code} error for {method} {path} due to global probability.")
        return simulated_error_code

    # TODO: Implement more granular error rules from storage["error_rules"] or config_manager
    # for rule in storage["error_rules"]:
    #     if rule["path_pattern"] in path and rule["method"] == method:
    #         if random.random() < rule.get("probability", 1.0):
    #             logger.warning(f"Simulating error based on rule: {rule}")
    #             return rule.get("error_code", 500)
    return None

def get_namespaced_key_util(namespace: str, key: str) -> str:
    """Combines namespace and key for storage."""
    return f"{namespace}:{key}"

def get_key_from_path_util(path: str) -> Optional[str]:
    """Extracts a key from the request path (e.g., /memory/retrieve/mykey)."""
    parts = path.strip('/').split('/')
    # Expecting format like /api/v1/atrian/memory/retrieve/{key} or /memory/store/{key}
    # Adjust indices based on your actual API structure
    if len(parts) >= 3 and parts[-2] in ["retrieve", "store", "delete"]:
        return parts[-1]
    elif len(parts) >= 2 and parts[-2] in ["retrieve", "store", "delete"]: # If no /api/v1/atrian prefix
        return parts[-1]
    # Don't log a warning for endpoints that are expected to not have keys in path
    if not (path.endswith("/memory/retrieve") or path.endswith("/memory/store") or 
            path.endswith("/memory/list") or path.endswith("/health")):
        logger.warning(f"Could not extract key from path: {path}")
    return None

logger.info("Helper functions for Mock API loaded.")

# --- End of Helper Functions Section --- 

# --- Main Request Handler Class ---
class EnhancedMockWindsurfAPIHandler(BaseHTTPRequestHandler):
    """
    Handles incoming HTTP requests for the Mock Windsurf API.
    Implements GET, POST, PUT, DELETE methods for memory operations
    and a health check endpoint.
    """

    def _handle_options(self):
        """Handles OPTIONS pre-flight requests for CORS."""
        send_response_util(self, 204, 'text/plain', b'') # No Content, ensure bytes

    def do_OPTIONS(self):
        self._handle_options()

    def _process_request(self, method_handler):
        """Common request processing logic."""
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        log_request_util(self, parsed_path, query_params)
        
        simulate_latency_util()
        
        simulated_error = should_simulate_error_util(parsed_path.path, self.command)
        if simulated_error:
            send_error_response_util(self, simulated_error, f"Simulated {simulated_error} error.")
            return
            
        method_handler(parsed_path, query_params)

    def do_GET(self):
        self._process_request(self._handle_get)

    def _handle_get(self, parsed_path, query_params):
        """Handles GET requests."""
        path = parsed_path.path
        namespace = config_manager.get_namespace()

        if path.endswith("/health"):
            health_status = {
                "status": "ok", 
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "service": "ATRiAN Mock Windsurf API",
                "version": "0.2.0",
                "active_environment": config_manager.current_environment
            }
            send_json_response_util(self, 200, health_status)
        
        elif "/memory/retrieve/" in path:
            key = get_key_from_path_util(path)
            if not key:
                send_error_response_util(self, 400, "Missing key in path for retrieve operation.")
                return
            
            namespaced_key = get_namespaced_key_util(namespace, key)
            item = storage["memory_items"].get(namespaced_key)
            if item:
                send_json_response_util(self, 200, item)
            else:
                send_error_response_util(self, 404, f"Key '{key}' not found in namespace '{namespace}'.")
        
        elif path.endswith("/memory/list"):
            items_in_namespace = {
                k.split(':', 1)[1]: v 
                for k, v in storage["memory_items"].items() 
                if k.startswith(namespace + ":")
            }
            send_json_response_util(self, 200, {"keys": list(items_in_namespace.keys()), "count": len(items_in_namespace)})

        elif path.endswith("/admin/logs"):
            send_json_response_util(self, 200, {"access_log": storage["access_log"][-100:]})
        
        else:
            send_error_response_util(self, 404, "Endpoint not found.")

    def do_POST(self):
        self._process_request(self._handle_post)

    def _handle_post(self, parsed_path, query_params):
        """Handles POST requests."""
        path = parsed_path.path
        namespace = config_manager.get_namespace()
        
        if "/memory/store" in path:
            body = parse_request_body(self)
            if not body:
                send_error_response_util(self, 400, "Invalid or missing JSON request body.")
                return

            key_from_path = get_key_from_path_util(path)
            key_from_body = body.get("key")
            
            if not (key_from_path or key_from_body):
                 send_error_response_util(self, 400, "Missing 'key' in request path or body for store operation.")
                 return

            key = key_from_path or key_from_body
            value = body.get("value")
            metadata = body.get("metadata", {})
            
            if "value" not in body:
                send_error_response_util(self, 400, "Missing 'value' in request body for store operation.")
                return

            namespaced_key = get_namespaced_key_util(namespace, key)
            storage["memory_items"][namespaced_key] = {"value": value, "metadata": metadata, "timestamp": datetime.utcnow().isoformat() + "Z"}
            logger.info(f"Stored item with key '{namespaced_key}' in namespace '{namespace}'.")
            send_json_response_util(self, 201, {"status": "created", "key": key, "namespace": namespace})

        elif path.endswith("/memory/retrieve"):
            body = parse_request_body(self)
            if not body:
                send_error_response_util(self, 400, "Invalid or missing JSON request body.")
                return

            key = body.get("key")
            if not key:
                send_error_response_util(self, 400, "Missing 'key' in request body for retrieve operation.")
                return

            # Log the key being requested for debugging
            logger.info(f"Attempting to retrieve item with key '{key}'")
            
            # Check if the key exists in storage
            if key in storage["memory_items"]:
                item = storage["memory_items"][key]
                logger.info(f"Retrieved item with key '{key}'")
                send_json_response_util(self, 200, item)
            else:
                # List all keys in storage for debugging
                available_keys = list(storage["memory_items"].keys())
                logger.warning(f"Key '{key}' not found. Available keys: {available_keys[:5]}{'...' if len(available_keys) > 5 else ''}")
                send_error_response_util(self, 404, f"Key '{key}' not found.")
                
        elif path.endswith("/admin/config/error_simulation"):
            body = parse_request_body(self)
            if body and "enable" in body:
                logger.info(f"Received error simulation config update: {body}")
                send_json_response_util(self, 200, {"status": "error_simulation_config_updated", "new_config": body})
            else:
                send_error_response_util(self, 400, "Invalid error simulation config.")
        else:
            send_error_response_util(self, 404, "Endpoint not found.")

    def do_PUT(self):
        self._process_request(self._handle_put)

    def _handle_put(self, parsed_path, query_params):
        """Handles PUT requests (similar to POST for full update)."""
        path = parsed_path.path
        namespace = config_manager.get_namespace()

        if "/memory/store/" in path or "/memory/update/" in path:
            key = get_key_from_path_util(path)
            if not key:
                send_error_response_util(self, 400, "Missing key in path for update operation.")
                return

            body = parse_request_body(self)
            if not body:
                send_error_response_util(self, 400, "Invalid or missing JSON request body.")
                return
            
            value = body.get("value")
            metadata = body.get("metadata", {})

            if "value" not in body:
                send_error_response_util(self, 400, "Missing 'value' in request body for update operation.")
                return

            namespaced_key = get_namespaced_key_util(namespace, key)
            if namespaced_key in storage["memory_items"]:
                storage["memory_items"][namespaced_key] = {"value": value, "metadata": metadata, "timestamp": datetime.utcnow().isoformat() + "Z"}
                logger.info(f"Updated item with key '{key}' in namespace '{namespace}'.")
                send_json_response_util(self, 200, {"status": "updated", "key": key, "namespace": namespace})
            else:
                send_error_response_util(self, 404, f"Key '{key}' not found for update in namespace '{namespace}'. Cannot update non-existent item.")
        else:
            send_error_response_util(self, 404, "Endpoint not found.")

    def do_DELETE(self):
        self._process_request(self._handle_delete)

    def _handle_delete(self, parsed_path, query_params):
        """Handles DELETE requests."""
        path = parsed_path.path
        namespace = config_manager.get_namespace()

        if "/memory/delete/" in path:
            key = get_key_from_path_util(path)
            if not key:
                send_error_response_util(self, 400, "Missing key in path for delete operation.")
                return
            
            namespaced_key = get_namespaced_key_util(namespace, key)
            if namespaced_key in storage["memory_items"]:
                del storage["memory_items"][namespaced_key]
                logger.info(f"Deleted item with key '{key}' from namespace '{namespace}'.")
                send_json_response_util(self, 200, {"status": "deleted", "key": key, "namespace": namespace})
            else:
                send_error_response_util(self, 404, f"Key '{key}' not found for delete in namespace '{namespace}'.")
        else:
            send_error_response_util(self, 404, "Endpoint not found.")

    def version_string(self):
        return "ATRiAN-Mock-API/0.2.0"

logger.info("EnhancedMockWindsurfAPIHandler class defined.")

# --- End of Request Handler Class Section ---

# --- Main Function and Server Execution ---

def run_server(server_class=HTTPServer, handler_class=EnhancedMockWindsurfAPIHandler, host=DEFAULT_HOST, port=DEFAULT_PORT):
    """
    Runs the HTTP server.
    
    Args:
        server_class: The server class to use (e.g., HTTPServer, ThreadingHTTPServer).
        handler_class: The request handler class.
        host (str): The hostname or IP address to bind to.
        port (int): The port number to bind to.
    """
    try:
        server_address = (host, port)
        httpd = server_class(server_address, handler_class)
        
        print_egos_banner(f"ATRiAN Mock API Server Running")
        logger.info(f"Server starting on http://{host}:{port}")
        logger.info(f"Serving API for namespace: {config_manager.get_namespace()}")
        logger.info(f"Log file: {LOG_FILE_NAME}")
        logger.info("Press Ctrl+C to stop the server.")
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Server shutting down (KeyboardInterrupt)...")
    except Exception as e:
        logger.error(f"Server failed to start or encountered an error: {e}", exc_info=True)
    finally:
        if 'httpd' in locals() and hasattr(httpd, 'server_close'):
            httpd.server_close()
        logger.info("Server stopped.")

if __name__ == "__main__":
    ATRIAN_API_ENV_VAR_NAME = "ATRIAN_API_ENV"  # Define the constant for env var name
    parser = argparse.ArgumentParser(description="ATRiAN Enhanced Mock Windsurf API Server")
    parser.add_argument("--host", type=str, default=os.environ.get("ATRIAN_MOCK_HOST", DEFAULT_HOST),
                        help=f"Hostname or IP to bind to (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=int(os.environ.get("ATRIAN_MOCK_PORT", DEFAULT_PORT)),
                        help=f"Port to bind to (default: {DEFAULT_PORT})")
    parser.add_argument("--env", type=str, default=os.environ.get(ATRIAN_API_ENV_VAR_NAME, config_manager.current_environment),
                        help=f"Configuration environment to use (default: {config_manager.current_environment})")
    
    args = parser.parse_args()

    if args.env != config_manager.current_environment:
        if not config_manager.switch_environment(args.env):
            logger.error(f"Could not switch to environment '{args.env}'. Exiting.")
            sys.exit(1)
        else:
             logger.info(f"Switched to environment '{args.env}' via command line argument.")

    run_server(host=args.host, port=args.port)

# --- End of Main Function and Server Execution ---