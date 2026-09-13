from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Addresses(AsyncBaseResource):
    """
    sangho.addresses.list(**criteria)
    sangho.addresses.retrieve(id)
    sangho.addresses.create(**payloads)
    sangho.addresses.update(id, **payloads)
    sangho.addresses.delete(id)
    sangho.addresses.options()
    """

    _path = "/addresses/"

    async def list(self, **criteria) -> list[dict]:
        self._client.assert_secret_key("addresses.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("addresses.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, **payloads) -> dict:
        self._client.assert_secret_key("addresses.create")
        return await self._client.post(self._path, body=payloads)

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("addresses.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def delete(self, id: str) -> None:
        self._client.assert_secret_key("addresses.delete")
        return await self._client.delete(f"{self._path}{id}/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
