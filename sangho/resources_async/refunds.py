from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Refunds(AsyncBaseResource):
    _path = "/refunds/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("refunds.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("refunds.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, transaction: str, **opts) -> dict:
        """
        Args:
            transaction: Transaction ID to refund.
            amount: Partial refund amount in XAF (omit for full refund).
            reason: optional.
        """
        self._client.assert_secret_key("refunds.create")
        return await self._client.post(self._path, body={"transaction": transaction, **opts})

    async def cancel(self, id: str) -> dict:
        self._client.assert_secret_key("refunds.cancel")
        return await self._client.post(f"{self._path}{id}/cancel/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
