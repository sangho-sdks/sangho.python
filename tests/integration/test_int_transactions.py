"""Tests d'intégration — Transactions"""

import pytest

from sangho import SanghoNotFoundError

pytestmark = pytest.mark.integration


class TestTransactionsIntegration:
    def test_list_transactions(self, client):
        result = client.transactions.list(page_size=5)
        assert "count" in result
        assert isinstance(result["results"], list)
        assert len(result["results"]) <= 5

    def test_list_transactions_ordered(self, client):
        result = client.transactions.list(ordering="-created_at", page_size=10)
        assert "results" in result

    def test_retrieve_nonexistent_raises(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.transactions.retrieve("trans_doesnotexist000")

    def test_options_returns_schema(self, client):
        schema = client.transactions.options()
        assert isinstance(schema, dict)
