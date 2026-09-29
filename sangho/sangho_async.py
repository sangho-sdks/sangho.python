"""
Sangho Python SDK — Async client.

Même surface d'API que ``sangho.Sangho``, en asynchrone (``await``) — pour
les applications construites sur asyncio (FastAPI, aiohttp, etc.). Utilise
``httpx.AsyncClient`` en interne au lieu du client bloquant.

Usage::

    import asyncio
    import sangho

    async def main():
        async with sangho.AsyncSangho("sk_test_xxx") as client:
            customer = await client.customers.create(
                email="jean@example.com", name="Jean Ondo"
            )
            intent = await client.payment_intents.create(
                amount=5000, customer=customer["id"]
            )
            print(intent["id"])

    asyncio.run(main())
"""

from __future__ import annotations

from sangho._http_async import AsyncHttpClient
from sangho.resources_async import (
    Account,
    Addresses,
    Apps,
    CheckoutSessions,
    Connect,
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


class AsyncSangho:
    """
    Async entry point for the Sangho API. Every resource method is a
    coroutine (``await client.customers.list()``), otherwise identical to
    the synchronous ``Sangho`` client.

    Args:
        api_key: Your Sangho API key (``sk_prod_``, ``sk_test_``, ``pk_prod_``, ``pk_test_``).
        base_url: Override the default API base URL.
        timeout: HTTP timeout in seconds (default 30).
        max_retries: Max retry attempts on 429/5xx responses and transient
            network/timeout errors (default 3).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.sangho.ga/v1",
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self._client = AsyncHttpClient(api_key, base_url, timeout, max_retries)

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
        self.connect = Connect(self._client)
        self.sandbox = Sandbox(self._client)

    # Identique à Sangho.construct_event — vérification de signature pure
    # (aucun I/O), donc pas besoin d'une version async dédiée.
    construct_event = staticmethod(Webhooks.construct_event)
    generate_test_header = staticmethod(Webhooks.generate_test_header)

    @property
    def api_key(self) -> str:
        return self._client.api_key

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncSangho:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        masked = self._client.api_key[:12] + "…"
        return f"AsyncSangho(api_key={masked!r})"
