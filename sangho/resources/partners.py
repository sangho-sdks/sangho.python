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

    def options(self) -> dict:
        return self._client.options(self._path)
