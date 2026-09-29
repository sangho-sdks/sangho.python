"""
Sangho SDK — HTTP client
Thin wrapper over httpx with retry logic (exponential back-off) for 429/5xx
and for transient network/timeout errors — mirrors the JS SDK's HttpClient
(@/core/http.ts) method for method.
"""

from __future__ import annotations

import time
import uuid
from typing import Any
from urllib.parse import urlparse

import httpx

from sangho._errors import (
    SanghoError,
    SanghoNetworkError,
    SanghoPublicKeyError,
    SanghoRateLimitError,
    SanghoTimeoutError,
    _raise_for_status,
)

SDK_VERSION = "0.1.4"

# Le backend distingue les clés de production ("prod") des clés de test
# ("test") — il n'existe pas de préfixe "live" côté API Sangho.
VALID_KEY_PREFIXES = ("pk_prod_", "sk_prod_", "pk_test_", "sk_test_")


def _validate_api_key(api_key: str) -> None:
    if not api_key or not isinstance(api_key, str):
        raise ValueError(
            "api_key must be a non-empty string. "
            "Find your API keys at https://dash.sangho.ga/project/api-keys."
        )
    if not any(api_key.startswith(prefix) for prefix in VALID_KEY_PREFIXES):
        raise ValueError(
            f'Invalid API key format: "{api_key[:10]}...". '
            f"Keys must start with one of: {', '.join(VALID_KEY_PREFIXES)}."
        )
    if len(api_key) < 20:
        raise ValueError("API key is too short.")


def _validate_base_url(base_url: str) -> None:
    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f'Invalid base_url: "{base_url}".')
    is_local = parsed.hostname in ("localhost", "127.0.0.1")
    if parsed.scheme != "https" and not is_local:
        raise ValueError(
            f'Refusing to send API keys over a non-HTTPS base_url: "{base_url}". '
            "Use an https:// URL (localhost/127.0.0.1 are exempt for local development)."
        )


class HttpClient:
    """Thread-safe HTTP client backed by httpx.Client."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.sangho.ga/v1",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        _validate_api_key(api_key)
        _validate_base_url(base_url)

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.key_type: str = "public" if api_key.startswith("pk_") else "secret"
        self.sandbox: bool = api_key.startswith("pk_test_") or api_key.startswith("sk_test_")
        self._timeout = timeout
        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"sangho-python/{SDK_VERSION}",
                "X-Sangho-SDK": f"python/{SDK_VERSION}",
                "X-Sangho-Environment": "sandbox" if self.sandbox else "live",
            },
        )

    # ------------------------------------------------------------------
    # Key guards
    # ------------------------------------------------------------------

    def assert_secret_key(self, method: str) -> None:
        """Raise SanghoPublicKeyError if the key is a public key."""
        if self.key_type == "public":
            raise SanghoPublicKeyError.for_method(method)

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

    def put(self, path: str, body: dict | None = None) -> Any:
        return self._request("PUT", path, json=body or {})

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
        attempt = 0

        while True:
            try:
                response = self._client.request(method, url, headers=extra_headers, **kwargs)
            except httpx.TimeoutException:
                if attempt < self.max_retries:
                    time.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise SanghoTimeoutError(self._timeout) from None
            except httpx.RequestError as exc:
                # Erreur réseau (DNS, connexion refusée, etc.) — jamais de
                # réponse du serveur. Transitoire : on retry comme un 5xx.
                if attempt < self.max_retries:
                    time.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise SanghoNetworkError(str(exc)) from None

            try:
                return self._handle_response(response)
            except SanghoError as err:
                if self._is_retryable(err) and attempt < self.max_retries:
                    # Un 429 avec Retry-After prime sur le backoff exponentiel.
                    if isinstance(err, SanghoRateLimitError) and err.retry_after:
                        delay: float = err.retry_after
                    else:
                        delay = self._backoff(attempt)
                    time.sleep(delay)
                    attempt += 1
                    continue
                raise

    @staticmethod
    def _backoff(attempt: int) -> float:
        return (2**attempt) * 0.5

    @staticmethod
    def _is_retryable(err: SanghoError) -> bool:
        """429 (rate limit) ou 5xx sont transitoires. Jamais les autres 4xx
        (400/401/403/404/409/422) — erreurs permanentes côté client."""
        if isinstance(err, SanghoRateLimitError):
            return True
        return isinstance(err.status_code, int) and err.status_code >= 500

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code == 204:
            return None
        try:
            data = response.json()
        except ValueError:
            data = {}
        if response.is_success:
            return data
        _raise_for_status(response, data)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
