"""
Tests d'intégration — PaymentIntents
Couvre : create, retrieve, list, confirm, cancel
"""

import pytest

from sangho import SanghoNotFoundError

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def payment_intent(client, test_customer):
    """Crée un payment intent de test."""
    intent = client.payment_intents.create(
        amount=10000,
        customer=test_customer["id"],
        description="Integration test payment",
    )
    yield intent
    # Annulation si pas encore terminé
    try:
        if intent.get("status") not in ("succeeded", "canceled"):
            client.payment_intents.cancel(intent["id"])
    except Exception:
        pass


class TestPaymentIntentsIntegration:
    def test_create_payment_intent(self, client, test_customer):
        """Crée un payment intent et vérifie la structure."""
        intent = client.payment_intents.create(
            amount=5000,
            customer=test_customer["id"],
        )
        assert intent["id"]
        assert intent["amount"] == 5000
        assert intent["customer"] == test_customer["id"]
        assert intent["status"] in ("requires_payment_method", "requires_confirmation", "created")
        assert "created_at" in intent

        client.payment_intents.cancel(intent["id"])

    def test_retrieve_payment_intent(self, client, payment_intent):
        retrieved = client.payment_intents.retrieve(payment_intent["id"])
        assert retrieved["id"] == payment_intent["id"]
        assert retrieved["amount"] == payment_intent["amount"]

    def test_list_payment_intents_paginated(self, client):
        result = client.payment_intents.list(page_size=5)
        assert "count" in result
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_list_filter_by_customer(self, client, test_customer, payment_intent):
        result = client.payment_intents.list(customer=test_customer["id"])
        ids = [pi["id"] for pi in result["results"]]
        assert payment_intent["id"] in ids

    def test_cancel_payment_intent(self, client, test_customer):
        intent = client.payment_intents.create(
            amount=2500,
            customer=test_customer["id"],
        )
        canceled = client.payment_intents.cancel(intent["id"])
        assert canceled["status"] == "canceled"
        assert canceled["id"] == intent["id"]

    def test_retrieve_nonexistent_raises_not_found(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.payment_intents.retrieve("pay_doesnotexist000")

    def test_options_returns_schema(self, client):
        schema = client.payment_intents.options()
        assert isinstance(schema, dict)
