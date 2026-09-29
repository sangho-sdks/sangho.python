"""Tests d'intégration — Invoices"""

import pytest

from sangho import SanghoNotFoundError

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def draft_invoice(client, test_customer):
    invoice = client.invoices.create(
        customer=test_customer["id"],
        amount=20000,
    )
    yield invoice
    try:
        client.invoices.delete(invoice["id"])
    except Exception:
        pass


class TestInvoicesIntegration:
    def test_create_invoice(self, client, test_customer):
        invoice = client.invoices.create(
            customer=test_customer["id"],
            amount=10000,
        )
        assert invoice["id"]
        assert invoice["amount"] == 10000
        assert invoice["customer"] == test_customer["id"]
        client.invoices.delete(invoice["id"])

    def test_retrieve_invoice(self, client, draft_invoice):
        retrieved = client.invoices.retrieve(draft_invoice["id"])
        assert retrieved["id"] == draft_invoice["id"]

    def test_list_invoices(self, client):
        result = client.invoices.list(page_size=5)
        assert "count" in result
        assert isinstance(result["data"], list)

    def test_void_invoice(self, client, test_customer):
        invoice = client.invoices.create(customer=test_customer["id"], amount=3000)
        voided = client.invoices.void(invoice["id"])
        assert voided.get("status") == "void"

    def test_retrieve_nonexistent_raises(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.invoices.retrieve("inv_doesnotexist000")
