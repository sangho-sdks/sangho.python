from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Subscriptions(AsyncBaseResource):
    _path = "/subscriptions/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("subscriptions.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("subscriptions.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, customer: str, plan: str, **opts) -> dict:
        self._client.assert_secret_key("subscriptions.create")
        return await self._client.post(
            self._path, body={"customer": customer, "plan": plan, **opts}
        )

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("subscriptions.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def cancel(self, id: str, **opts) -> dict:
        """Cancel at period end or immediately."""
        self._client.assert_secret_key("subscriptions.cancel")
        return await self._client.post(f"{self._path}{id}/cancel/", body=opts)

    async def pause(self, id: str) -> dict:
        self._client.assert_secret_key("subscriptions.pause")
        return await self._client.post(f"{self._path}{id}/pause/")

    async def resume(self, id: str) -> dict:
        self._client.assert_secret_key("subscriptions.resume")
        return await self._client.post(f"{self._path}{id}/resume/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
