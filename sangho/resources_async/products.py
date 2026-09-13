from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Products(AsyncBaseResource):
    _path = "/products/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("products.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("products.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, name: str, price: int, **opts) -> dict:
        """
        Args:
            name: Product name.
            price: Amount in XAF (integer).
            description, currency, metadata: optional.
        """
        self._client.assert_secret_key("products.create")
        return await self._client.post(self._path, body={"name": name, "price": price, **opts})

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("products.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def delete(self, id: str) -> None:
        self._client.assert_secret_key("products.delete")
        return await self._client.delete(f"{self._path}{id}/")

    async def archive(self, id: str) -> dict:
        self._client.assert_secret_key("products.archive")
        return await self._client.post(f"{self._path}{id}/archive/")

    async def restore(self, id: str) -> dict:
        self._client.assert_secret_key("products.restore")
        return await self._client.post(f"{self._path}{id}/restore/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
