"""Tests d'intégration — PaymentLinks"""

import pytest

from sangho import SanghoNotFoundError

pytestmark = pytest.mark.integration


class TestPaymentLinksIntegration:
    def test_create_payment_link(self, client):
        link = client.payment_links.create(amount=15_000)
        assert link["id"]
        assert link["amount"] == 15_000
        client.payment_links.archive(link["id"])

    def test_list_payment_links(self, client):
        result = client.payment_links.list(page_size=5)
        assert "count" in result
        assert isinstance(result["data"], list)

    def test_retrieve_nonexistent_raises(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.payment_links.retrieve("pl_doesnotexist000")

    def test_options_returns_schema(self, client):
        schema = client.payment_links.options()
        assert isinstance(schema, dict)
