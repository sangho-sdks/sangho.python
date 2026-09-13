from __future__ import annotations

from sangho._base import BaseResource


class Addresses(BaseResource):
    """
    sangho.addresses.list(**criteria)
    sangho.addresses.retrieve(id)
    sangho.addresses.create(**payloads)
    sangho.addresses.update(id, **payloads)
    sangho.addresses.delete(id)
    sangho.addresses.options()
    """

    _path = "/addresses/"

    def list(self, **criteria) -> list[dict]:
        self._client.assert_secret_key("addresses.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("addresses.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, **payloads) -> dict:
        self._client.assert_secret_key("addresses.create")
        return self._client.post(self._path, body=payloads)

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("addresses.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def delete(self, id: str) -> None:
        self._client.assert_secret_key("addresses.delete")
        return self._client.delete(f"{self._path}{id}/")

    def options(self) -> dict:
        return self._client.options(self._path)
