"""
Sangho Python SDK — Main client.

Usage::

    import sangho

    client = sangho.Sangho("sk_test_xxx")
    customers = client.customers.list(status="active")
    customer  = client.customers.create(email="jean@example.com", name="Jean Ondo")
"""
from __future__ import annotations

from sangho._http import HttpClient
from sangho.resources import (
    Apps, Customers, Products, PaymentIntents, PaymentLinks,
    CheckoutSessions, Invoices, Transactions, Refunds, Subscriptions,
    PaymentMethods, Receipts, Webhooks, Security, Partners,
)


class Sangho:
    """
    Main entry point for the Sangho API.

    Args:
        api_key: Your Sangho API key (``sk_live_``, ``sk_test_``, ``pk_live_``, ``pk_test_``).
        base_url: Override the default API base URL.
        timeout: HTTP timeout in seconds (default 30).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.sangho.com/v1",
        timeout: int = 30,
    ) -> None:
        self._client = HttpClient(api_key, base_url, timeout)

        self.apps               = Apps(self._client)
        self.customers          = Customers(self._client)
        self.products           = Products(self._client)
        self.payment_intents    = PaymentIntents(self._client)
        self.payment_links      = PaymentLinks(self._client)
        self.checkout_sessions  = CheckoutSessions(self._client)
        self.invoices           = Invoices(self._client)
        self.transactions       = Transactions(self._client)
        self.refunds            = Refunds(self._client)
        self.subscriptions      = Subscriptions(self._client)
        self.payment_methods    = PaymentMethods(self._client)
        self.receipts           = Receipts(self._client)
        self.webhooks           = Webhooks(self._client)
        self.security           = Security(self._client)
        self.partners           = Partners(self._client)

    @property
    def api_key(self) -> str:
        return self._client.api_key

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def __enter__(self) -> "Sangho":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def __repr__(self) -> str:
        masked = self._client.api_key[:12] + "…"
        return f"Sangho(api_key={masked!r})"
