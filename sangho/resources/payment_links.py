from __future__ import annotations

from sangho._base import BaseResource


class PaymentLinks(BaseResource):
    _path = "/payment-links/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("payment_links.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("payment_links.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, amount: int, **opts) -> dict:
        self._client.assert_secret_key("payment_links.create")
        return self._client.post(self._path, body={"amount": amount, **opts})

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("payment_links.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def delete(self, id: str) -> dict:
        self._client.assert_secret_key("payment_links.delete")
        return self._client.delete(f"{self._path}{id}/")

    def archive(self, id: str) -> dict:
        self._client.assert_secret_key("payment_links.archive")
        return self._client.post(f"{self._path}{id}/archive/")

    def restore(self, id: str) -> dict:
        self._client.assert_secret_key("payment_links.restore")
        return self._client.post(f"{self._path}{id}/restore/")

    def options(self) -> dict:
        return self._client.options(self._path)
