"""Base resource class shared by all async resource modules."""

from __future__ import annotations

from sangho._http_async import AsyncHttpClient


class AsyncBaseResource:
    """Holds a reference to the shared AsyncHttpClient."""

    def __init__(self, client: AsyncHttpClient) -> None:
        self._client = client
