"""
Sangho SDK — Async HTTP client
Async twin of ``sangho._http.HttpClient``: same validation, retry policy
(exponential back-off on 429/5xx + transient network/timeout errors), and
error mapping — backed by ``httpx.AsyncClient`` / ``asyncio.sleep`` instead
of the blocking ``httpx.Client`` / ``time.sleep``.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import httpx

from sangho._errors import (
    SanghoError,
    SanghoNetworkError,
    SanghoPublicKeyError,
    SanghoRateLimitError,
    SanghoTimeoutError,
    _raise_for_status,
)
from sangho._http import SDK_VERSION, _validate_api_key, _validate_base_url


class AsyncHttpClient:
    """Thread-safe async HTTP client backed by httpx.AsyncClient."""

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
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"sangho-python/{SDK_VERSION}",
                "X-Sangho-SDK": f"python-async/{SDK_VERSION}",
                "X-Sangho-Environment": "sandbox" if self.sandbox else "live",
            },
        )

    # ------------------------------------------------------------------
    # Key guards
    # ------------------------------------------------------------------

    def assert_secret_key(self, method: str) -> None:
        if self.key_type == "public":
            raise SanghoPublicKeyError.for_method(method)

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------

    async def get(self, path: str, params: dict | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(
        self, path: str, body: dict | None = None, idempotency_key: str | None = None
    ) -> Any:
        """POST avec en-tête ``Idempotency-Key``. La clé peut être fournie en argument ou via
        ``idempotency_key=`` dans les options de n'importe quelle méthode d'écriture ; sans clé, une
        nouvelle est générée. Sans clé fournie, un POST n'est PAS rejoué après un timeout / une
        erreur réseau (le serveur a pu traiter la requête : risque de doublon, PY-03)."""
        body = dict(body or {})
        explicit = idempotency_key or body.pop("idempotency_key", None)
        return await self._request(
            "POST",
            path,
            json=body,
            headers={"Idempotency-Key": explicit or str(uuid.uuid4())},
            _retry_transport=bool(explicit),
        )

    async def put(self, path: str, body: dict | None = None) -> Any:
        return await self._request("PUT", path, json=body or {})

    async def patch(self, path: str, body: dict) -> Any:
        return await self._request("PATCH", path, json=body)

    async def delete(self, path: str) -> Any:
        return await self._request("DELETE", path)

    async def options(self, path: str) -> Any:
        return await self._request("OPTIONS", path)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        extra_headers: dict = kwargs.pop("headers", {})
        # Timeout / erreur réseau : on ne rejoue pas un POST sans clé d'idempotence fournie par l'appelant
        retry_transport: bool = kwargs.pop("_retry_transport", True)
        attempt = 0

        while True:
            try:
                response = await self._client.request(method, url, headers=extra_headers, **kwargs)
            except httpx.TimeoutException:
                if retry_transport and attempt < self.max_retries:
                    await asyncio.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise SanghoTimeoutError(self._timeout) from None
            except httpx.RequestError as exc:
                if retry_transport and attempt < self.max_retries:
                    await asyncio.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise SanghoNetworkError(str(exc)) from None

            try:
                return self._handle_response(response)
            except SanghoError as err:
                if self._is_retryable(err) and attempt < self.max_retries:
                    if isinstance(err, SanghoRateLimitError) and err.retry_after:
                        delay: float = err.retry_after
                    else:
                        delay = self._backoff(attempt)
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue
                raise

    @staticmethod
    def _backoff(attempt: int) -> float:
        return (2**attempt) * 0.5

    @staticmethod
    def _is_retryable(err: SanghoError) -> bool:
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

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncHttpClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
