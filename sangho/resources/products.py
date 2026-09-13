from __future__ import annotations

from sangho._base import BaseResource


class Products(BaseResource):
    _path = "/products/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("products.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("products.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, name: str, price: int, **opts) -> dict:
        """
        Args:
            name: Product name.
            price: Amount in XAF (integer).
            description, currency, metadata: optional.
        """
        self._client.assert_secret_key("products.create")
        return self._client.post(self._path, body={"name": name, "price": price, **opts})

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("products.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def delete(self, id: str) -> None:
        self._client.assert_secret_key("products.delete")
        return self._client.delete(f"{self._path}{id}/")

    def archive(self, id: str) -> dict:
        self._client.assert_secret_key("products.archive")
        return self._client.post(f"{self._path}{id}/archive/")

    def restore(self, id: str) -> dict:
        self._client.assert_secret_key("products.restore")
        return self._client.post(f"{self._path}{id}/restore/")

    def options(self) -> dict:
        return self._client.options(self._path)
