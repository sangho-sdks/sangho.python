from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Apps(AsyncBaseResource):
    _path = "/apps/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("apps.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("apps.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, name: str, **opts) -> dict:
        self._client.assert_secret_key("apps.create")
        return await self._client.post(self._path, body={"name": name, **opts})

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("apps.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def delete(self, id: str) -> None:
        self._client.assert_secret_key("apps.delete")
        return await self._client.delete(f"{self._path}{id}/")

    async def keys(self, id: str) -> dict:
        """Retrieve the current publishable/secret key pair for an app."""
        self._client.assert_secret_key("apps.keys")
        return await self._client.get(f"{self._path}{id}/keys/")

    async def roll_secret(self, id: str) -> dict:
        """Rotate the secret key for an app."""
        self._client.assert_secret_key("apps.roll_secret")
        return await self._client.post(f"{self._path}{id}/roll-secret/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
