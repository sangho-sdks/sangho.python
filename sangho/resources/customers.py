from __future__ import annotations
from sangho._base import BaseResource


class Customers(BaseResource):
    """
    Manage customers.

    sangho.customers.list(**criteria)
    sangho.customers.retrieve(id)
    sangho.customers.create(email, name, **opts)
    sangho.customers.update(id, **payloads)
    sangho.customers.delete(id)
    sangho.customers.options()
    sangho.customers.list_transactions(id, **criteria)
    """

    _path = "/customers/"

    def list(self, **criteria) -> dict:
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
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        """Retrieve a single customer by ID."""
        self._client.assert_secret_key("customers.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, email: str, name: str, **opts) -> dict:
        """
        Create a customer.

        Args:
            email: Customer email (unique per app).
            name: Full name — split into firstname/lastname backend-side.
            phone: International phone number (optional).
            metadata: Arbitrary key/value pairs (optional).
        """
        self._client.assert_secret_key("customers.create")
        return self._client.post(self._path, body={"email": email, "name": name, **opts})

    def update(self, id: str, **payloads) -> dict:
        """Partial update (PATCH). All fields optional."""
        self._client.assert_secret_key("customers.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def delete(self, id: str) -> None:
        """Hard delete. Returns None (HTTP 204)."""
        self._client.assert_secret_key("customers.delete")
        return self._client.delete(f"{self._path}{id}/")

    def options(self) -> dict:
        """DRF schema metadata."""
        return self._client.options(self._path)

    def list_transactions(self, id: str, **criteria) -> dict:
        """List all transactions for a given customer."""
        self._client.assert_secret_key("customers.list_transactions")
        return self._client.get(f"{self._path}{id}/transactions/", params=criteria or None)
