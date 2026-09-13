from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class PaymentIntents(AsyncBaseResource):
    _path = "/payment-intents/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("payment_intents.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("payment_intents.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, amount: int, customer: str, **opts) -> dict:
        """
        Args:
            amount: Amount in XAF.
            customer: Customer ID.
            payment_method, description, metadata, capture_method: optional.
        """
        self._client.assert_secret_key("payment_intents.create")
        return await self._client.post(
            self._path, body={"amount": amount, "customer": customer, **opts}
        )

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("payment_intents.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def confirm(self, id: str, **payloads) -> dict:
        """Confirm a payment intent."""
        self._client.assert_secret_key("payment_intents.confirm")
        return await self._client.post(f"{self._path}{id}/confirm/", body=payloads)

    async def capture(self, id: str, **payloads) -> dict:
        """Capture an authorized payment intent."""
        self._client.assert_secret_key("payment_intents.capture")
        return await self._client.post(f"{self._path}{id}/capture/", body=payloads)

    async def cancel(self, id: str, **payloads) -> dict:
        """Cancel a payment intent."""
        self._client.assert_secret_key("payment_intents.cancel")
        return await self._client.post(f"{self._path}{id}/cancel/", body=payloads)

    async def options(self) -> dict:
        return await self._client.options(self._path)
