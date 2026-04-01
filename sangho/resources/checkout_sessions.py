from __future__ import annotations
from sangho._base import BaseResource


class CheckoutSessions(BaseResource):
    _path = "/checkout-sessions/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("checkout_sessions.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("checkout_sessions.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, amount: int, success_url: str, cancel_url: str, **opts) -> dict:
        """
        Args:
            amount: Amount in XAF.
            success_url: Redirect URL on success.
            cancel_url: Redirect URL on cancel.
        """
        self._client.assert_secret_key("checkout_sessions.create")
        return self._client.post(
            self._path,
            body={"amount": amount, "success_url": success_url, "cancel_url": cancel_url, **opts},
        )

    def expire(self, id: str) -> dict:
        self._client.assert_secret_key("checkout_sessions.expire")
        return self._client.post(f"{self._path}{id}/expire/")

    def options(self) -> dict:
        return self._client.options(self._path)
