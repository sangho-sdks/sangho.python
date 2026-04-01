"""
Tests for the Sangho Python SDK.
Uses respx to mock httpx calls — no real network requests.
"""
import json
import pytest
import respx
import httpx

import sangho
from sangho import (
    Sangho,
    SanghoAuthError,
    SanghoNotFoundError,
    SanghoPublicKeyError,
    SanghoValidationError,
    SanghoRateLimitError,
)

BASE = "https://api.sangho.com/v1"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return Sangho("sk_test_abc123456789")


@pytest.fixture
def pub_client():
    return Sangho("pk_test_abc123456789")


# ---------------------------------------------------------------------------
# Key validation
# ---------------------------------------------------------------------------

def test_invalid_key_prefix():
    with pytest.raises(ValueError, match="Invalid API key format"):
        Sangho("bad_key_123")


def test_public_key_on_write(pub_client):
    with pytest.raises(SanghoPublicKeyError):
        pub_client.customers.list()


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@respx.mock
def test_customers_list(client):
    payload = {"count": 1, "next": None, "previous": None, "results": [{"id": "cust_1"}]}
    respx.get(f"{BASE}/customers/").mock(return_value=httpx.Response(200, json=payload))
    result = client.customers.list()
    assert result["count"] == 1
    assert result["results"][0]["id"] == "cust_1"


@respx.mock
def test_customers_retrieve(client):
    respx.get(f"{BASE}/customers/cust_1/").mock(
        return_value=httpx.Response(200, json={"id": "cust_1", "email": "jean@example.com"})
    )
    customer = client.customers.retrieve("cust_1")
    assert customer["email"] == "jean@example.com"


@respx.mock
def test_customers_create(client):
    body = {"id": "cust_2", "email": "marie@example.com", "name": "Marie Nzé"}
    respx.post(f"{BASE}/customers/").mock(return_value=httpx.Response(201, json=body))
    customer = client.customers.create(email="marie@example.com", name="Marie Nzé")
    assert customer["id"] == "cust_2"


@respx.mock
def test_customers_delete(client):
    respx.delete(f"{BASE}/customers/cust_1/").mock(return_value=httpx.Response(204))
    result = client.customers.delete("cust_1")
    assert result is None


# ---------------------------------------------------------------------------
# Payment Intents
# ---------------------------------------------------------------------------

@respx.mock
def test_payment_intent_create_and_confirm(client):
    intent = {"id": "pay_1", "status": "requires_confirmation", "amount": 5000}
    confirmed = {"id": "pay_1", "status": "succeeded", "amount": 5000}
    respx.post(f"{BASE}/payment-intents/").mock(return_value=httpx.Response(201, json=intent))
    respx.post(f"{BASE}/payment-intents/pay_1/confirm/").mock(
        return_value=httpx.Response(200, json=confirmed)
    )
    i = client.payment_intents.create(amount=5000, customer="cust_1")
    assert i["status"] == "requires_confirmation"
    c = client.payment_intents.confirm(i["id"])
    assert c["status"] == "succeeded"


# ---------------------------------------------------------------------------
# Webhooks — signature verification
# ---------------------------------------------------------------------------

def test_webhook_construct_event_valid():
    import hashlib, hmac, time
    secret = "whsec_testsecret"
    ts = str(int(time.time()))
    payload = b'{"type":"payment_intent.succeeded"}'
    signed = f"{ts}.".encode() + payload
    sig = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    header = f"t={ts},v1={sig}"
    event = sangho.resources.webhooks.Webhooks.construct_event(payload, header, secret)  # type: ignore[attr-defined]
    assert event["type"] == "payment_intent.succeeded"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

@respx.mock
def test_401_raises_auth_error(client):
    respx.get(f"{BASE}/customers/").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )
    with pytest.raises(SanghoAuthError):
        client.customers.list()


@respx.mock
def test_404_raises_not_found(client):
    respx.get(f"{BASE}/customers/bad_id/").mock(
        return_value=httpx.Response(404, json={"message": "Not found"})
    )
    with pytest.raises(SanghoNotFoundError):
        client.customers.retrieve("bad_id")


@respx.mock
def test_422_raises_validation_error(client):
    respx.post(f"{BASE}/customers/").mock(
        return_value=httpx.Response(
            422,
            json={"message": "Validation error", "detail": {"email": ["This field is required."]}},
        )
    )
    with pytest.raises(SanghoValidationError) as exc_info:
        client.customers.create(email="", name="Test")
    assert "email" in exc_info.value.field_errors


@respx.mock
def test_429_raises_rate_limit(client):
    respx.get(f"{BASE}/customers/").mock(
        return_value=httpx.Response(429, json={"message": "Rate limit", "retry_later": 30})
    )
    with pytest.raises(SanghoRateLimitError) as exc_info:
        # Disable retry for test speed
        client._client._RETRY_DELAYS = ()  # type: ignore
        client.customers.list()


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------

def test_context_manager():
    with Sangho("sk_test_abc123456789") as c:
        assert c._client is not None
