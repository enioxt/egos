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

# - @references {C:\EGOS\ATRiAN\memory\windsurf_api_backend.py}
# - @references {C:\EGOS\ATRiAN\memory\windsurf_memory_adapter.py}
# - @references {C:\EGOS\ATRiAN\memory\demo_memory_integration.py}
# --- 

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mock_api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mock_windsurf_api")

# In-memory storage for the mock API
storage = {
    "memory_items": {},  # key -> {value, metadata}
    "access_log": []     # List of access records
}

class MockWindsurfAPIHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the mock Windsurf API.
    Simulates the endpoints expected by WindsurfAPIBackend.
    """
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """Set response headers."""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def _send_json_response(self, data, status_code=200):
        """Send a JSON response."""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data).encode())
    
    def _log_request(self, endpoint, method, params=None, body=None):
        """Log request details."""
        storage["access_log"].append({
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "params": params,
            "body": body,
        })
        logger.info(f"Request: {method} {endpoint} - Params: {params}")
    
    def do_GET(self):
        """Handle GET requests."""
        url = urlparse(self.path)
        path = url.path.rstrip('/')
        query_params = parse_qs(url.query)
        
        # Convert all query parameters from lists to single values
        params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        
        self._log_request(path, "GET", params)
        
        # Health check endpoint
        if path == '/api/v1/atrian/health':
            self._send_json_response({"status": "healthy", "version": "1.0.0"})
            return
            
        # Memory retrieval endpoint
        elif path == '/api/v1/atrian/memory/retrieve':
            key = params.get('key')
            if key and key in storage["memory_items"]:
                self._send_json_response({
                    "success": True,
                    "data": storage["memory_items"][key]["value"],
                    "metadata": storage["memory_items"][key]["metadata"]
                })
            else:
                self._send_json_response({
                    "success": False,
                    "error": "Key not found"
                }, 404)
            return
            
        # Memory list endpoint
        elif path == '/api/v1/atrian/memory/list':
            prefix = params.get('prefix', '')
            # Filter keys by the provided prefix
            matching_keys = [k for k in storage["memory_items"].keys() if k.startswith(prefix)]
            self._send_json_response({
                "success": True,
                "keys": matching_keys
            })
            return
        
        # Not found
        self._send_json_response({
            "success": False,
            "error": "Endpoint not found"
        }, 404)
    
    def do_POST(self):
        """Handle POST requests."""
        url = urlparse(self.path)
        path = url.path.rstrip('/')
        
        # Read JSON request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            body = json.loads(post_data)
            self._log_request(path, "POST", None, body)
            
            # Memory storage endpoint
            if path == '/api/v1/atrian/memory/store':
                key = body.get('key')
                value = body.get('value')
                metadata = body.get('metadata', {})
                
                if not key:
                    self._send_json_response({
                        "success": False,
                        "error": "Key is required"
                    }, 400)
                    return
                    
                # Ensure metadata has timestamp
                if 'timestamp' not in metadata:
                    metadata['timestamp'] = datetime.now().isoformat()
                    
                # Store in memory
                storage["memory_items"][key] = {
                    "value": value,
                    "metadata": metadata
                }
                
                self._send_json_response({
                    "success": True,
                    "key": key
                })
                return
                
            # Not found
            self._send_json_response({
                "success": False,
                "error": "Endpoint not found"
            }, 404)
                
        except json.JSONDecodeError:
            self._send_json_response({
                "success": False,
                "error": "Invalid JSON"
            }, 400)
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        url = urlparse(self.path)
        path = url.path.rstrip('/')
        query_params = parse_qs(url.query)
        
        # Convert all query parameters from lists to single values
        params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        
        self._log_request(path, "DELETE", params)
        
        # Memory deletion endpoint
        if path == '/api/v1/atrian/memory/delete':
            key = params.get('key')
            if not key:
                # Try to get key from request body
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    try:
                        body = json.loads(post_data)
                        key = body.get('key')
                    except json.JSONDecodeError:
                        pass
            
            if key and key in storage["memory_items"]:
                del storage["memory_items"][key]
                self._send_json_response({
                    "success": True,
                    "deleted": key
                })
            else:
                self._send_json_response({
                    "success": False,
                    "error": "Key not found"
                }, 404)
            return
            
        # Memory clearing endpoint
        elif path == '/api/v1/atrian/memory/clear':
            prefix = params.get('prefix', '')
            # Filter and delete keys by the provided prefix
            keys_to_delete = [k for k in storage["memory_items"].keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                del storage["memory_items"][key]
                
            self._send_json_response({
                "success": True,
                "deleted_count": len(keys_to_delete)
            })
            return
            
        # Not found
        self._send_json_response({
            "success": False,
            "error": "Endpoint not found"
        }, 404)
    
    def log_message(self, format, *args):
        """Override log_message to use our logger."""
        logger.info("%s - - [%s] %s" % (self.client_address[0],
                                         self.log_date_time_string(),
                                         format % args))

def run_mock_api_server(port=8000):
    """Run the mock API server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockWindsurfAPIHandler)
    logger.info(f"Starting mock Windsurf API server on port {port}")
    logger.info(f"API base URL: http://localhost:{port}/api/v1/atrian/")
    logger.info("Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    httpd.server_close()
    logger.info("Server stopped")

def print_banner(title: str) -> None:
    """Print a formatted banner with the given title."""
    width = 80
    padding = (width - len(title) - 4) // 2
    print("\n" + "=" * width)
    print(" " * padding + f"| {title} |")
    print("=" * width + "\n")

if __name__ == "__main__":
    print_banner("ATRiAN Mock Windsurf API Server")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Mock Windsurf API Server for testing WindsurfAPIBackend")
    parser.add_argument('-p', '--port', type=int, default=8000, help='Port to run the server on (default: 8000)')
    args = parser.parse_args()
    
    try:
        # Run the server
        run_mock_api_server(port=args.port)
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        import traceback
        traceback.print_exc()