from __future__ import annotations
from sangho._base import BaseResource


class Receipts(BaseResource):
    _path = "/receipts/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("receipts.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("receipts.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def send(self, id: str, email: str | None = None) -> dict:
        """Send receipt by email."""
        self._client.assert_secret_key("receipts.send")
        body = {"email": email} if email else {}
        return self._client.post(f"{self._path}{id}/send/", body=body)

    def options(self) -> dict:
        return self._client.options(self._path)
