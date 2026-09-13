"""Base resource class shared by all resource modules."""

from __future__ import annotations

from sangho._http import HttpClient


class BaseResource:
    """Holds a reference to the shared HttpClient."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client
