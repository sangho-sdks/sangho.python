"""Tests d'intégration — Refunds"""

import pytest

from sangho import SanghoNotFoundError

pytestmark = pytest.mark.integration


class TestRefundsIntegration:
    def test_list_refunds(self, client):
        result = client.refunds.list(page_size=5)
        assert "count" in result
        assert isinstance(result["results"], list)

    def test_retrieve_nonexistent_raises(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.refunds.retrieve("ref_doesnotexist000")

    def test_options_returns_schema(self, client):
        schema = client.refunds.options()
        assert isinstance(schema, dict)
