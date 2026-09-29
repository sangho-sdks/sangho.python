from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class PaymentMethods(AsyncBaseResource):
    _path = "/payment-methods/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("payment_methods.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("payment_methods.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def set_default(self, id: str) -> dict:
        self._client.assert_secret_key("payment_methods.set_default")
        return await self._client.post(f"{self._path}{id}/set-default/")

    async def attach(self, id: str, customer: str) -> dict:
        self._client.assert_secret_key("payment_methods.attach")
        return await self._client.post(f"{self._path}{id}/attach/", body={"customer": customer})

    async def detach(self, id: str) -> dict:
        self._client.assert_secret_key("payment_methods.detach")
        return await self._client.post(f"{self._path}{id}/detach/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
