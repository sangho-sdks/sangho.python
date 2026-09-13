from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Transactions(AsyncBaseResource):
    _path = "/transactions/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("transactions.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("transactions.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("transactions.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def cancel(self, id: str) -> dict:
        self._client.assert_secret_key("transactions.cancel")
        return await self._client.post(f"{self._path}{id}/cancel/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
