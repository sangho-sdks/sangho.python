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

    def get_pdf_url(self, id: str) -> dict:
        """Return a signed, expiring URL to the receipt PDF: {"url", "expires_at"}."""
        self._client.assert_secret_key("receipts.get_pdf_url")
        return self._client.get(f"{self._path}{id}/pdf/")

    def options(self) -> dict:
        return self._client.options(self._path)
