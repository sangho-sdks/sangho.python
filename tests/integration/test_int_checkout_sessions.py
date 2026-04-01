"""Tests d'intégration — CheckoutSessions"""
import pytest
from sangho import SanghoNotFoundError

pytestmark = pytest.mark.integration


class TestCheckoutSessionsIntegration:

    def test_create_checkout_session(self, client):
        session = client.checkout_sessions.create(
            amount=20_000,
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        assert session["id"]
        assert session["amount"] == 20_000
        client.checkout_sessions.expire(session["id"])

    def test_list_checkout_sessions(self, client):
        result = client.checkout_sessions.list(page_size=5)
        assert "count" in result
        assert isinstance(result["results"], list)

    def test_retrieve_nonexistent_raises(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.checkout_sessions.retrieve("cs_doesnotexist000")

    def test_options_returns_schema(self, client):
        schema = client.checkout_sessions.options()
        assert isinstance(schema, dict)
