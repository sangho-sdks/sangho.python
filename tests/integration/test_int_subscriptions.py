"""Tests d'intégration — Subscriptions"""
import pytest
from sangho import SanghoNotFoundError

pytestmark = pytest.mark.integration


class TestSubscriptionsIntegration:

    def test_list_subscriptions(self, client):
        result = client.subscriptions.list(page_size=5)
        assert "count" in result
        assert isinstance(result["results"], list)

    def test_retrieve_nonexistent_raises(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.subscriptions.retrieve("sub_doesnotexist000")

    def test_options_returns_schema(self, client):
        schema = client.subscriptions.options()
        assert isinstance(schema, dict)
