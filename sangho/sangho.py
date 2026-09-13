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
    Account,
    Addresses,
    Apps,
    CheckoutSessions,
    Customers,
    Invoices,
    Partners,
    PaymentIntents,
    PaymentLinks,
    PaymentMethods,
    Products,
    Receipts,
    Refunds,
    Sandbox,
    Security,
    Subscriptions,
    Terminal,
    Transactions,
    Webhooks,
)


class Sangho:
    """
    Main entry point for the Sangho API.

    Args:
        api_key: Your Sangho API key (``sk_prod_``, ``sk_test_``, ``pk_prod_``, ``pk_test_``).
        base_url: Override the default API base URL.
        timeout: HTTP timeout in seconds (default 30).
        max_retries: Max retry attempts on 429/5xx responses and transient
            network/timeout errors (default 3).

    Example::

        # Côté serveur — clé secrète
        client = Sangho("sk_prod_xxx")
        intent = client.payment_intents.create(amount=5000, customer="cust_xxx")

        # Côté navigateur — clé publique (checkout uniquement)
        client = Sangho("pk_prod_xxx")
        session = client.checkout_sessions.retrieve("cs_xxx")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.sangho.ga/v1",
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self._client = HttpClient(api_key, base_url, timeout, max_retries)

        self.account = Account(self._client)
        self.addresses = Addresses(self._client)
        self.apps = Apps(self._client)
        self.customers = Customers(self._client)
        self.products = Products(self._client)
        self.payment_intents = PaymentIntents(self._client)
        self.payment_links = PaymentLinks(self._client)
        self.checkout_sessions = CheckoutSessions(self._client)
        self.invoices = Invoices(self._client)
        self.transactions = Transactions(self._client)
        self.refunds = Refunds(self._client)
        self.subscriptions = Subscriptions(self._client)
        self.payment_methods = PaymentMethods(self._client)
        self.receipts = Receipts(self._client)
        self.webhooks = Webhooks(self._client)
        self.security = Security(self._client)
        self.partners = Partners(self._client)
        self.terminal = Terminal(self._client)
        self.sandbox = Sandbox(self._client)

    # Vérifie et parse un événement webhook entrant (signature HMAC-SHA256 +
    # protection anti-replay). Exposé au niveau du client, comme en JS
    # (`Sangho.constructEvent`), en plus de `Webhooks.construct_event`.
    #
    # Example::
    #
    #     event = Sangho.construct_event(
    #         request.body, request.headers["Sangho-Signature"], WEBHOOK_SECRET
    #     )
    #     if event["type"] == "payment_intent.succeeded":
    #         fulfill_order(event["data"])
    construct_event = staticmethod(Webhooks.construct_event)

    @property
    def api_key(self) -> str:
        return self._client.api_key

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def __enter__(self) -> Sangho:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def __repr__(self) -> str:
        masked = self._client.api_key[:12] + "…"
        return f"Sangho(api_key={masked!r})"
