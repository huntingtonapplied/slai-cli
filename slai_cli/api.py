"""SLAI API client — thin wrapper around httpx."""

import json
import os
import time
from typing import Any, Dict, Generator, Optional, Tuple

import httpx

from slai_cli.config import get_api_key, get_api_url, load_config
from slai_cli.log import logger

# Retry configuration
MAX_RETRIES = int(os.getenv("SLAI_MAX_RETRIES", "3"))
RETRY_BACKOFF_BASE = 1.0  # seconds
RETRY_BACKOFF_MAX = 30.0  # seconds
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
RETRYABLE_EXCEPTIONS = (httpx.ConnectError, httpx.TimeoutException)


# Error suggestion hints keyed by status code + context
_ERROR_HINTS = {
    401: [
        "Run: slai login",
        "Or set SLAI_API_KEY env var",
    ],
    403: [
        "You may not have access to this resource.",
        "Check permissions or contact your organization admin.",
    ],
    404: [
        "The resource was not found. Check the ID or URL.",
        "Run: slai loads list   to see available loads",
    ],
    422: [
        "The request data is invalid. Check required fields.",
        "Run: slai <command> --help   for usage details",
    ],
    429: [
        "Rate limit exceeded. Wait a moment and try again.",
    ],
    500: [
        "Server error. The SLAI team has been notified.",
        "Try again in a few minutes.",
    ],
}


def format_error_hint(status_code: int, detail: Optional[str] = None) -> str:
    """Get actionable hint text for an error status code."""
    if status_code == 403 and detail and "Active subscription required" in detail:
        hints = [
            "An active subscription or entitlement is required for this action.",
            "Subscribe or redeem an access code at /checkout.",
        ]
    else:
        hints = _ERROR_HINTS.get(status_code, [])
    if not hints:
        return ""
    return "\n".join(f"  {h}" for h in hints)


class AuthError(Exception):
    pass


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class SLAIClient:
    """HTTP client for the SLAI API."""

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or get_api_key()
        self.api_url = api_url or get_api_url()

        if not self.api_key:
            raise AuthError(
                "Not authenticated.\n"
                "  Run: slai login\n"
                "  Or set SLAI_API_KEY env var"
            )

        config = load_config()
        self._timeout = float(os.getenv("SLAI_TIMEOUT", config.get("timeout", 60)))
        self._client = httpx.Client(
            base_url=self.api_url,
            timeout=self._timeout,
        )
        logger.debug("API client initialized: %s (timeout=%.0fs)", self.api_url, self._timeout)

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"ApiKey {self.api_key}"
        return headers

    def _request_with_retry(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Execute an HTTP request with retry logic for transient failures."""
        last_exc = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = getattr(self._client, method)(path, headers=self._headers(), **kwargs)
                if resp.status_code not in RETRYABLE_STATUS_CODES or attempt == MAX_RETRIES:
                    return resp
                delay = min(RETRY_BACKOFF_BASE * (2 ** attempt), RETRY_BACKOFF_MAX)
                logger.info(
                    "Retrying %s %s (status %d, attempt %d/%d, waiting %.1fs)",
                    method.upper(), path, resp.status_code, attempt + 1, MAX_RETRIES, delay,
                )
                time.sleep(delay)
            except RETRYABLE_EXCEPTIONS as exc:
                last_exc = exc
                if attempt == MAX_RETRIES:
                    if isinstance(exc, httpx.ConnectError):
                        raise APIError(
                            f"Cannot connect to {self.api_url}\n"
                            "  Check your network connection\n"
                            "  Verify API URL: slai doctor",
                            status_code=0,
                        ) from exc
                    raise
                delay = min(RETRY_BACKOFF_BASE * (2 ** attempt), RETRY_BACKOFF_MAX)
                logger.info(
                    "Retrying %s %s (%s, attempt %d/%d, waiting %.1fs)",
                    method.upper(), path, exc.__class__.__name__, attempt + 1, MAX_RETRIES, delay,
                )
                time.sleep(delay)
        raise last_exc or APIError(f"Request failed after {MAX_RETRIES} retries")

    def get(self, path: str, params: Optional[Dict] = None) -> Any:
        logger.debug("GET %s params=%s", path, params)
        resp = self._request_with_retry("get", path, params=params)
        return self._handle_response(resp)

    def post(self, path: str, data: Optional[Dict] = None) -> Any:
        logger.debug("POST %s", path)
        resp = self._request_with_retry("post", path, json=data)
        return self._handle_response(resp)

    def put(self, path: str, data: Optional[Dict] = None) -> Any:
        logger.debug("PUT %s", path)
        resp = self._request_with_retry("put", path, json=data)
        return self._handle_response(resp)

    def delete(self, path: str) -> Any:
        logger.debug("DELETE %s", path)
        resp = self._request_with_retry("delete", path)
        if resp.status_code == 204:
            return None
        return self._handle_response(resp)

    def _handle_response(self, resp: httpx.Response) -> Any:
        logger.debug("Response %d (%s)", resp.status_code, resp.request.url)
        if resp.status_code == 401:
            raise AuthError(
                "Not authenticated.\n"
                "  Run: slai login\n"
                "  Or set SLAI_API_KEY env var"
            )
        if resp.status_code == 409:
            data = resp.json()
            raise APIError(
                data.get("detail", "Conflict"),
                status_code=409,
            )
        if resp.status_code >= 400:
            detail = ""
            try:
                body = resp.json()
                detail = body.get("detail", "")
                if isinstance(detail, dict):
                    detail = detail.get("message", str(detail))
                if not detail:
                    detail = resp.text
            except Exception:
                detail = resp.text

            hint = format_error_hint(resp.status_code, detail)
            msg = f"API error {resp.status_code}: {detail}"
            if hint:
                msg += f"\n{hint}"
            raise APIError(msg, status_code=resp.status_code)

        return resp.json()

    # Load operations
    def list_loads(self, params: Optional[Dict] = None) -> list:
        """List loads."""
        data = self.get("/loads", params=params)
        return data.get("data", data) if isinstance(data, dict) else data

    def get_load(self, load_id: str) -> dict:
        """Get a specific load."""
        return self.get(f"/loads/{load_id}")

    def create_load(self, data: dict) -> dict:
        """Create a new load."""
        return self.post("/loads", data)

    def update_load(self, load_id: str, data: dict) -> dict:
        """Update a load."""
        return self.put(f"/loads/{load_id}", data)

    def delete_load(self, load_id: str) -> None:
        """Delete a load."""
        self.delete(f"/loads/{load_id}")

    # Shipment operations
    def list_shipments(self, params: Optional[Dict] = None) -> list:
        """List shipments."""
        data = self.get("/shipments", params=params)
        return data.get("data", data) if isinstance(data, dict) else data

    def get_shipment(self, shipment_id: str) -> dict:
        """Get a specific shipment."""
        return self.get(f"/shipments/{shipment_id}")

    # Metrics operations
    def get_portfolio_metrics(self) -> dict:
        """Get portfolio metrics."""
        return self.get("/metrics/portfolio")

    # Organization operations
    def list_organizations(self, load_id: str) -> list:
        """List organizations for a load."""
        data = self.get(f"/loads/{load_id}/organizations")
        return data.get("data", data) if isinstance(data, dict) else data

    # API key operations
    def list_api_keys(self) -> list:
        """List all API keys for the current organization."""
        data = self.get("/v1/developer/keys")
        return data.get("keys", [])

    def create_api_key(self, name: str, scopes: list, expires_in_days: Optional[int] = None) -> dict:
        """Create a new API key. Returns the full key (shown once only)."""
        payload: Dict[str, Any] = {"name": name, "scopes": scopes}
        if expires_in_days is not None:
            payload["expires_in_days"] = expires_in_days
        return self.post("/v1/developer/keys", payload)

    def revoke_api_key(self, key_id: str) -> None:
        """Revoke an API key by ID."""
        self.delete(f"/v1/developer/keys/{key_id}")
