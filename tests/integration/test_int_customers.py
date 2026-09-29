"""
Tests d'intégration — Customers
Couvre : list, retrieve, create, update, delete
"""

import uuid

import pytest

from sangho import SanghoNotFoundError, SanghoPublicKeyError, SanghoValidationError

pytestmark = pytest.mark.integration


class TestCustomersIntegration:
    # ── CRUD complet ─────────────────────────────────────────────────────────

    def test_create_customer(self, client):
        """Crée un client et vérifie la structure de la réponse."""
        email = f"test-create-{uuid.uuid4().hex[:8]}@sangho-test.com"
        customer = client.customers.create(email=email, name="Jean Ondo")

        assert customer["id"].startswith("cust_") or len(customer["id"]) > 0
        assert customer["email"] == email
        assert customer["name"] == "Jean Ondo"
        assert "created_at" in customer
        assert "status" in customer

        # Nettoyage
        client.customers.delete(customer["id"])

    def test_retrieve_customer(self, client, test_customer):
        """Récupère un client existant par son ID."""
        retrieved = client.customers.retrieve(test_customer["id"])

        assert retrieved["id"] == test_customer["id"]
        assert retrieved["email"] == test_customer["email"]

    def test_list_customers_returns_paginated(self, client):
        """list() retourne une réponse paginée valide."""
        result = client.customers.list(page_size=5)

        assert "count" in result
        assert "data" in result
        assert "next" in result
        assert "previous" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) <= 5

    def test_list_customers_filter_by_status(self, client):
        """Filtre par statut active."""
        result = client.customers.list(status="active", page_size=10)

        assert "data" in result
        for c in result["data"]:
            assert c.get("status") == "active"

    def test_list_customers_search(self, client, test_customer):
        """Recherche full-text par email."""
        result = client.customers.list(search=test_customer["email"])

        ids = [c["id"] for c in result["data"]]
        assert test_customer["id"] in ids

    def test_update_customer(self, client, test_customer):
        """Met à jour le numéro de téléphone d'un client."""
        updated = client.customers.update(
            test_customer["id"],
            phone="+24177999999",
        )
        assert updated["id"] == test_customer["id"]
        assert updated["phone"] == "+24177999999"

    def test_delete_customer_returns_none(self, client):
        """delete() retourne None (HTTP 204)."""
        email = f"test-del-{uuid.uuid4().hex[:8]}@sangho-test.com"
        customer = client.customers.create(email=email, name="À supprimer")
        result = client.customers.delete(customer["id"])
        assert result is None

    # ── Erreurs ───────────────────────────────────────────────────────────────

    def test_retrieve_nonexistent_raises_not_found(self, client):
        with pytest.raises(SanghoNotFoundError) as exc:
            client.customers.retrieve("cust_doesnotexist000")
        assert exc.value.status_code == 404

    def test_create_duplicate_email_raises_validation(self, client, test_customer):
        """Créer deux clients avec le même email doit échouer."""
        with pytest.raises(SanghoValidationError) as exc:
            client.customers.create(
                email=test_customer["email"],
                name="Duplicate",
            )
        assert exc.value.status_code == 422

    def test_create_invalid_email_raises_validation(self, client):
        with pytest.raises(SanghoValidationError) as exc:
            client.customers.create(email="not-an-email", name="Bad Email")
        assert "email" in exc.value.field_errors

    def test_public_key_cannot_list_customers(self, pub_client):
        with pytest.raises(SanghoPublicKeyError):
            pub_client.customers.list()

    # ── Options (DRF metadata) ────────────────────────────────────────────────

    def test_options_returns_schema(self, client):
        schema = client.customers.options()
        assert isinstance(schema, dict)
        assert "name" in schema or "actions" in schema
