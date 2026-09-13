"""Tests d'intégration — Products"""

import uuid

import pytest

from sangho import SanghoNotFoundError

pytestmark = pytest.mark.integration


class TestProductsIntegration:
    def test_create_product(self, client):
        product = client.products.create(
            name=f"Produit Test {uuid.uuid4().hex[:6]}",
            price=15000,
            description="Créé par les tests d'intégration",
        )
        assert product["id"]
        assert product["price"] == 15000
        assert "created_at" in product
        client.products.delete(product["id"])

    def test_retrieve_product(self, client, test_product):
        retrieved = client.products.retrieve(test_product["id"])
        assert retrieved["id"] == test_product["id"]
        assert retrieved["name"] == test_product["name"]

    def test_list_products(self, client):
        result = client.products.list(page_size=5)
        assert "count" in result
        assert isinstance(result["results"], list)

    def test_update_product_price(self, client, test_product):
        updated = client.products.update(test_product["id"], price=9999)
        assert updated["price"] == 9999

    def test_archive_and_restore(self, client):
        product = client.products.create(name=f"Archive Test {uuid.uuid4().hex[:6]}", price=1000)
        archived = client.products.archive(product["id"])
        assert archived.get("status") in ("archived", "inactive")

        restored = client.products.restore(product["id"])
        assert restored.get("status") in ("active",)
        client.products.delete(product["id"])

    def test_delete_nonexistent_raises(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.products.retrieve("prod_doesnotexist000")
