from __future__ import annotations
from sangho._base import BaseResource


class Invoices(BaseResource):
    _path = "/invoices/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("invoices.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, customer: str, **opts) -> dict:
        self._client.assert_secret_key("invoices.create")
        return self._client.post(self._path, body={"customer": customer, **opts})

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("invoices.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def delete(self, id: str) -> None:
        self._client.assert_secret_key("invoices.delete")
        return self._client.delete(f"{self._path}{id}/")

    def pay(self, id: str, **payloads) -> dict:
        """Trigger payment for a draft invoice."""
        self._client.assert_secret_key("invoices.pay")
        return self._client.post(f"{self._path}{id}/pay/", body=payloads)

    def finalize(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.finalize")
        return self._client.post(f"{self._path}{id}/finalize/")

    def void(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.void")
        return self._client.post(f"{self._path}{id}/void/")

    def mark_uncollectible(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.mark_uncollectible")
        return self._client.post(f"{self._path}{id}/mark-uncollectible/")

    def send_invoice(self, id: str) -> dict:
        self._client.assert_secret_key("invoices.send_invoice")
        return self._client.post(f"{self._path}{id}/send/")

    def options(self) -> dict:
        return self._client.options(self._path)
