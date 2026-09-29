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

    async def get_pdf_url(self, id: str) -> dict:
        """Return a signed, expiring URL to the receipt PDF: {"url", "expires_at"}."""
        self._client.assert_secret_key("receipts.get_pdf_url")
        return await self._client.get(f"{self._path}{id}/pdf/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
