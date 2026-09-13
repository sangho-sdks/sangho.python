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

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("transactions.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def cancel(self, id: str) -> dict:
        self._client.assert_secret_key("transactions.cancel")
        return self._client.post(f"{self._path}{id}/cancel/")

    def options(self) -> dict:
        return self._client.options(self._path)
