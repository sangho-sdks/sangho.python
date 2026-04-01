"""
Sangho Python SDK — Integration tests
======================================
Ces tests tournent contre un vrai serveur Sangho (local ou sandbox).

Variables d'environnement requises :
    SANGHO_TEST_SECRET_KEY   sk_test_xxx  (obligatoire)
    SANGHO_TEST_PUBLIC_KEY   pk_test_xxx  (obligatoire)
    SANGHO_API_BASE_URL      https://api.sangho.com/v1  (optionnel)

Lancement :
    SANGHO_TEST_SECRET_KEY=sk_test_xxx pytest tests/integration/ -v
    # ou via Makefile :
    make test-integration
"""
import os
import pytest
from sangho import Sangho

# ── Skip global si clé absente ────────────────────────────────────────────────
def pytest_collection_modifyitems(items):
    if not os.getenv("SANGHO_TEST_SECRET_KEY"):
        skip = pytest.mark.skip(reason="SANGHO_TEST_SECRET_KEY not set — integration tests skipped")
        for item in items:
            if "integration" in str(item.fspath):
                item.add_marker(skip)


@pytest.fixture(scope="session")
def secret_key() -> str:
    key = os.getenv("SANGHO_TEST_SECRET_KEY", "")
    if not key:
        pytest.skip("SANGHO_TEST_SECRET_KEY not set")
    return key


@pytest.fixture(scope="session")
def public_key() -> str:
    key = os.getenv("SANGHO_TEST_PUBLIC_KEY", "")
    if not key:
        pytest.skip("SANGHO_TEST_PUBLIC_KEY not set")
    return key


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("SANGHO_API_BASE_URL", "https://api.sangho.com/v1")


@pytest.fixture(scope="session")
def client(secret_key, base_url) -> Sangho:
    return Sangho(api_key=secret_key, base_url=base_url)


@pytest.fixture(scope="session")
def pub_client(public_key, base_url) -> Sangho:
    return Sangho(api_key=public_key, base_url=base_url)


# ── Données de test réutilisables (nettoyées après session) ───────────────────
@pytest.fixture(scope="session")
def test_customer(client) -> dict:
    """Crée un client de test et le supprime après la session."""
    import uuid
    customer = client.customers.create(
        email=f"integration-test-{uuid.uuid4().hex[:8]}@sangho-test.com",
        name="Integration Test User",
        phone="+24177000000",
    )
    yield customer
    try:
        client.customers.delete(customer["id"])
    except Exception:
        pass


@pytest.fixture(scope="session")
def test_product(client) -> dict:
    """Crée un produit de test et le supprime après la session."""
    import uuid
    product = client.products.create(
        name=f"Test Product {uuid.uuid4().hex[:6]}",
        price=5000,
        description="Integration test product",
    )
    yield product
    try:
        client.products.delete(product["id"])
    except Exception:
        pass
