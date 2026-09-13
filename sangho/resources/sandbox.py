from __future__ import annotations

from sangho._base import BaseResource


class Sandbox(BaseResource):
    """
    sangho.sandbox.reset()
    """

    def reset(self) -> dict:
        """
        Delete all sandbox data for the current app (customers, products,
        payment_intents, transactions, refunds, invoices, checkout_sessions,
        subscriptions, payment_methods, receipts).

        The app itself, its API keys, and its settings are preserved.
        Blocked backend-side if the key used is a live key (``sk_prod_*``).

        Example:
            client.sandbox.reset()
        """
        self._client.assert_secret_key("sandbox.reset")
        return self._client.post("/reset/")
