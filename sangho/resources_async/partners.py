from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Partners(AsyncBaseResource):
    _path = "/partners/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("partners.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("partners.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, name: str, **opts) -> dict:
        self._client.assert_secret_key("partners.create")
        return await self._client.post(self._path, body={"name": name, **opts})

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("partners.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def delete(self, id: str) -> None:
        self._client.assert_secret_key("partners.delete")
        return await self._client.delete(f"{self._path}{id}/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
