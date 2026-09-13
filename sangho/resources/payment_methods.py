from __future__ import annotations

from sangho._base import BaseResource


class PaymentMethods(BaseResource):
    _path = "/payment-methods/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("payment_methods.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("payment_methods.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, type: str, **opts) -> dict:
        self._client.assert_secret_key("payment_methods.create")
        return self._client.post(self._path, body={"type": type, **opts})

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("payment_methods.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def delete(self, id: str) -> None:
        self._client.assert_secret_key("payment_methods.delete")
        return self._client.delete(f"{self._path}{id}/")

    def set_default(self, id: str) -> dict:
        self._client.assert_secret_key("payment_methods.set_default")
        return self._client.post(f"{self._path}{id}/set-default/")

    def attach(self, id: str, customer: str) -> dict:
        self._client.assert_secret_key("payment_methods.attach")
        return self._client.post(f"{self._path}{id}/attach/", body={"customer": customer})

    def detach(self, id: str) -> dict:
        self._client.assert_secret_key("payment_methods.detach")
        return self._client.post(f"{self._path}{id}/detach/")

    def options(self) -> dict:
        return self._client.options(self._path)
