"""
Sangho SDK — HTTP client
Thin wrapper over httpx with retry logic (exponential back-off) for 429/5xx.
"""
from __future__ import annotations

import time
import uuid
from typing import Any

import httpx

from sangho._errors import _raise_for_status, SanghoPublicKeyError

_RETRY_DELAYS = (0.5, 1.0, 2.0)  # seconds


class HttpClient:
    """Thread-safe HTTP client backed by httpx.Client."""

    def __init__(self, api_key: str, base_url: str = "https://api.sangho.com/v1", timeout: int = 30):
        if not api_key:
            raise ValueError("api_key must not be empty.")
        valid_prefixes = ("pk_live_", "sk_live_", "pk_test_", "sk_test_")
        if not any(api_key.startswith(p) for p in valid_prefixes):
            raise ValueError(
                f"Invalid API key format. Expected prefix: {valid_prefixes}"
            )
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.key_type: str = "public" if api_key.startswith("pk_") else "secret"
        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "sangho-python/1.0.0",
            },
        )

    # ------------------------------------------------------------------
    # Key guards
    # ------------------------------------------------------------------

    def assert_secret_key(self, method: str) -> None:
        """Raise SanghoPublicKeyError if the key is a public key."""
        if self.key_type == "public":
            raise SanghoPublicKeyError(method)

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, body: dict | None = None) -> Any:
        idempotency_key = str(uuid.uuid4())
        return self._request(
            "POST", path, json=body or {}, headers={"Idempotency-Key": idempotency_key}
        )

    def patch(self, path: str, body: dict) -> Any:
        return self._request("PATCH", path, json=body)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    def options(self, path: str) -> Any:
        return self._request("OPTIONS", path)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        extra_headers: dict = kwargs.pop("headers", {})

        for attempt, delay in enumerate((*_RETRY_DELAYS, None)):
            response = self._client.request(
                method, url, headers=extra_headers, **kwargs
            )
            if response.status_code in (429, 500, 502, 503, 504) and delay is not None:
                time.sleep(delay)
                continue
            return self._handle_response(response)

        # Final attempt — let it raise
        return self._handle_response(
            self._client.request(method, url, headers=extra_headers, **kwargs)
        )

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code == 204:
            return None
        data = response.json()
        if response.is_success:
            return data
        _raise_for_status(response, data)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
