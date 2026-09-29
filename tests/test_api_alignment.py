"""
Alignement avec l'API Sangho réelle (backend/api). Chaque test correspond à une route du backend ;
les méthodes retirées appelaient des routes inexistantes (404/405) et ne doivent pas revenir.
"""

import httpx
import pytest
import respx

from sangho import AsyncSangho, Sangho

BASE = "https://api.sangho.ga/v1"


@pytest.fixture
def client():
    return Sangho("sk_test_abc123456789")


@respx.mock
def test_subscriptions_reactivate(client):
    route = respx.post(f"{BASE}/subscriptions/sub_1/reactivate/").mock(
        return_value=httpx.Response(200, json={"id": "sub_1"})
    )
    assert client.subscriptions.reactivate("sub_1")["id"] == "sub_1"
    assert route.called


@respx.mock
@pytest.mark.parametrize("action", ["enable", "disable"])
def test_webhooks_enable_disable(client, action):
    route = respx.post(f"{BASE}/webhooks/wh_1/{action}/").mock(
        return_value=httpx.Response(200, json={"id": "wh_1"})
    )
    assert getattr(client.webhooks, action)("wh_1")["id"] == "wh_1"
    assert route.called


@respx.mock
def test_payment_intents_delete_is_cancel(client):
    route = respx.delete(f"{BASE}/payment-intents/pi_1/").mock(
        return_value=httpx.Response(200, json={"id": "pi_1", "status": "canceled"})
    )
    assert client.payment_intents.delete("pi_1")["status"] == "canceled"
    assert route.called


@respx.mock
def test_webhooks_retrieve_delivery(client):
    route = respx.get(f"{BASE}/webhooks/wh_1/deliveries/dlv_1/").mock(
        return_value=httpx.Response(200, json={"id": "dlv_1"})
    )
    assert client.webhooks.retrieve_delivery("wh_1", "dlv_1")["id"] == "dlv_1"
    assert route.called


@respx.mock
def test_receipts_pdf_url(client):
    respx.get(f"{BASE}/receipts/rcp_1/pdf/").mock(
        return_value=httpx.Response(
            200, json={"url": "https://x/y.pdf", "expires_at": "2026-01-01T00:00:00Z"}
        )
    )
    assert client.receipts.get_pdf_url("rcp_1")["url"].endswith(".pdf")


@respx.mock
def test_customer_payment_methods_use_the_customer_filter(client):
    route = respx.get(f"{BASE}/payment-methods/", params={"customer": "cus_1"}).mock(
        return_value=httpx.Response(
            200, json={"count": 0, "next": None, "previous": None, "data": []}
        )
    )
    assert client.customers.list_payment_methods("cus_1")["data"] == []
    assert route.called


@respx.mock
def test_list_responses_use_data_key(client):
    respx.get(f"{BASE}/products/").mock(
        return_value=httpx.Response(
            200, json={"count": 1, "next": None, "previous": None, "data": [{"id": "p1"}]}
        )
    )
    assert client.products.list()["data"][0]["id"] == "p1"


@pytest.mark.parametrize(
    ("resource", "method"),
    [
        ("apps", "roll_secret"),
        ("customers", "list_transactions"),
        ("invoices", "finalize"),
        ("partners", "create"),
        ("partners", "update"),
        ("partners", "delete"),
        ("payment_methods", "create"),
        ("payment_methods", "update"),
        ("payment_methods", "delete"),
        ("products", "archive"),
        ("products", "restore"),
        ("receipts", "send"),
        ("refunds", "update"),
        ("security", "roll_secret_key"),
        ("security", "list_sessions"),
        ("security", "revoke_session"),
    ],
)
def test_phantom_endpoints_are_gone(client, resource, method):
    assert not hasattr(getattr(client, resource), method)


@respx.mock
@pytest.mark.asyncio
async def test_async_reactivate_and_enable():
    respx.post(f"{BASE}/subscriptions/sub_1/reactivate/").mock(
        return_value=httpx.Response(200, json={"id": "sub_1"})
    )
    respx.post(f"{BASE}/webhooks/wh_1/enable/").mock(
        return_value=httpx.Response(200, json={"id": "wh_1"})
    )
    async with AsyncSangho("sk_test_abc123456789") as client:
        assert (await client.subscriptions.reactivate("sub_1"))["id"] == "sub_1"
        assert (await client.webhooks.enable("wh_1"))["id"] == "wh_1"
