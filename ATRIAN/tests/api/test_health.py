"""Simple pytest health check for ATRiAN EaaS API.
Run with: pytest -q tests/api/test_health.py
"""
# 
# @references:
#   - ATRIAN/tests/api/test_health.py

import os
from typing import Optional

import requests

API_URL = os.getenv("EAAS_API_URL", "http://127.0.0.1:8000")

def _url(path: str) -> str:
    return f"{API_URL.rstrip('/')}{path}"


def test_health_endpoint() -> None:
    """Validate /health returns success 200 and expected payload."""
    response: Optional[requests.Response] = None
    try:
        response = requests.get(_url("/health"), timeout=5)
    except Exception as exc:
        pytest.fail(f"Request to EaaS API failed: {exc}")

    assert response is not None, "No response returned"
    assert response.status_code == 200, f"Unexpected status: {response.status_code}"
    payload = response.json()
    assert payload.get("status") == "success"
    assert "EaaS API is running" in payload.get("message", "")