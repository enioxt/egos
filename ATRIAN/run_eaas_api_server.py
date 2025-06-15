#!/usr/bin/env python3
"""
ATRiAN EaaS API Server Runner
-----------------------------

This script runs the ATRiAN Ethics as a Service (EaaS) API server.

Usage:
    python run_eaas_api_server.py

Author: EGOS Team
Version: 1.0.0
Date: 2025-06-01
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import uvicorn

if __name__ == "__main__":
    print("Starting ATRiAN Ethics as a Service (EaaS) API server...")
    print("Access the API documentation at http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop the server")
    uvicorn.run("eaas_api:app", host="127.0.0.1", port=8000, reload=True)