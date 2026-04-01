"""Tests d'intégration — PaymentMethods"""
import pytest
from sangho import SanghoNotFoundError

pytestmark = pytest.mark.integration


class TestPaymentMethodsIntegration:

    def test_list_payment_methods(self, client):
        result = client.payment_methods.list(page_size=5)
        assert "count" in result
        assert isinstance(result["results"], list)

    def test_retrieve_nonexistent_raises(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.payment_methods.retrieve("pm_doesnotexist000")

    def test_options_returns_schema(self, client):
        schema = client.payment_methods.options()
        assert isinstance(schema, dict)
