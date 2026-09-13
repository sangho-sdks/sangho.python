from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class PaymentLinks(AsyncBaseResource):
    _path = "/payment-links/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("payment_links.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("payment_links.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, amount: int, **opts) -> dict:
        self._client.assert_secret_key("payment_links.create")
        return await self._client.post(self._path, body={"amount": amount, **opts})

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("payment_links.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def delete(self, id: str) -> dict:
        self._client.assert_secret_key("payment_links.delete")
        return await self._client.delete(f"{self._path}{id}/")

    async def archive(self, id: str) -> dict:
        self._client.assert_secret_key("payment_links.archive")
        return await self._client.post(f"{self._path}{id}/archive/")

    async def restore(self, id: str) -> dict:
        self._client.assert_secret_key("payment_links.restore")
        return await self._client.post(f"{self._path}{id}/restore/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
