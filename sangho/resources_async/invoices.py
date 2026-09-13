from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Invoices(AsyncBaseResource):
    _path = "/invoices/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("invoices.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, customer: str, **opts) -> dict:
        self._client.assert_secret_key("invoices.create")
        return await self._client.post(self._path, body={"customer": customer, **opts})

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("invoices.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def delete(self, id: str) -> None:
        self._client.assert_secret_key("invoices.delete")
        return await self._client.delete(f"{self._path}{id}/")

    async def pay(self, id: str, **payloads) -> dict:
        """Trigger payment for a draft invoice."""
        self._client.assert_secret_key("invoices.pay")
        return await self._client.post(f"{self._path}{id}/pay/", body=payloads)

    async def finalize(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.finalize")
        return await self._client.post(f"{self._path}{id}/finalize/")

    async def void(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.void")
        return await self._client.post(f"{self._path}{id}/void/")

    async def mark_uncollectible(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.mark_uncollectible")
        return await self._client.post(f"{self._path}{id}/mark-uncollectible/")

    async def send_invoice(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.send_invoice")
        return await self._client.post(f"{self._path}{id}/send/")

    async def get_pdf_url(self, id: str) -> dict:
        """Return a signed, expiring URL to the invoice PDF: {"url", "expires_at"}."""
        self._client.assert_secret_key("invoices.get_pdf_url")
        return await self._client.get(f"{self._path}{id}/pdf/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
