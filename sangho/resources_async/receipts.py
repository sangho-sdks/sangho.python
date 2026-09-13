from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Receipts(AsyncBaseResource):
    _path = "/receipts/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("receipts.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("receipts.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def send(self, id: str, email: str | None = None) -> dict:
        """Send receipt by email."""
        self._client.assert_secret_key("receipts.send")
        body = {"email": email} if email else {}
        return await self._client.post(f"{self._path}{id}/send/", body=body)

    async def options(self) -> dict:
        return await self._client.options(self._path)
