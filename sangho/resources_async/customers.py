from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Customers(AsyncBaseResource):
    """
    Manage customers.

    sangho.customers.list(**criteria)
    sangho.customers.retrieve(id)
    sangho.customers.create(email, name, **opts)
    sangho.customers.update(id, **payloads)
    sangho.customers.delete(id)
    sangho.customers.options()
    sangho.customers.list_transactions(id, **criteria)
    sangho.customers.list_payment_methods(id)
    """

    _path = "/customers/"

    async def list(self, **criteria) -> dict:
        """
        List customers with optional filters.

        Args:
            search: Full-text search on email/name
            status: "active" | "inactive" | "blocked"
            ordering: e.g. "-created_at"
            page: Page number (default 1)
            page_size: Items per page (default 20, max 100)

        Returns:
            {"count": int, "next": str|None, "previous": str|None, "results": [...]}
        """
        self._client.assert_secret_key("customers.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        """Retrieve a single customer by ID."""
        self._client.assert_secret_key("customers.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, email: str, name: str, **opts) -> dict:
        """
        Create a customer.

        Args:
            email: Customer email (unique per app).
            name: Full name — split into firstname/lastname backend-side.
            phone: International phone number (optional).
            metadata: Arbitrary key/value pairs (optional).
        """
        self._client.assert_secret_key("customers.create")
        return await self._client.post(self._path, body={"email": email, "name": name, **opts})

    async def update(self, id: str, **payloads) -> dict:
        """Partial update (PATCH). All fields optional."""
        self._client.assert_secret_key("customers.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def delete(self, id: str) -> None:
        """Hard delete. Returns None (HTTP 204)."""
        self._client.assert_secret_key("customers.delete")
        return await self._client.delete(f"{self._path}{id}/")

    async def options(self) -> dict:
        """DRF schema metadata."""
        return await self._client.options(self._path)

    async def list_transactions(self, id: str, **criteria) -> dict:
        """List all transactions for a given customer."""
        self._client.assert_secret_key("customers.list_transactions")
        return await self._client.get(f"{self._path}{id}/transactions/", params=criteria or None)

    async def list_payment_methods(self, id: str) -> dict:
        """List all payment methods attached to a given customer."""
        self._client.assert_secret_key("customers.list_payment_methods")
        return await self._client.get(f"{self._path}{id}/payment-methods/")
