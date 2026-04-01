from __future__ import annotations
from sangho._base import BaseResource


class Transactions(BaseResource):
    _path = "/transactions/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("transactions.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("transactions.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def options(self) -> dict:
        return self._client.options(self._path)
