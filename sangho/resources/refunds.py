from __future__ import annotations
from sangho._base import BaseResource


class Refunds(BaseResource):
    _path = "/refunds/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("refunds.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("refunds.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, transaction: str, **opts) -> dict:
        """
        Args:
            transaction: Transaction ID to refund.
            amount: Partial refund amount in XAF (omit for full refund).
            reason: optional.
        """
        self._client.assert_secret_key("refunds.create")
        return self._client.post(self._path, body={"transaction": transaction, **opts})

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("refunds.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def cancel(self, id: str) -> dict:
        self._client.assert_secret_key("refunds.cancel")
        return self._client.post(f"{self._path}{id}/cancel/")

    def options(self) -> dict:
        return self._client.options(self._path)
