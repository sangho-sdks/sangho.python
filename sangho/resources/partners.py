from __future__ import annotations
from sangho._base import BaseResource


class Partners(BaseResource):
    _path = "/partners/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("partners.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("partners.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, name: str, **opts) -> dict:
        self._client.assert_secret_key("partners.create")
        return self._client.post(self._path, body={"name": name, **opts})

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("partners.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def delete(self, id: str) -> None:
        self._client.assert_secret_key("partners.delete")
        return self._client.delete(f"{self._path}{id}/")

    def options(self) -> dict:
        return self._client.options(self._path)
