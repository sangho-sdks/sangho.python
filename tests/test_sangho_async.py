"""
Tests for AsyncSangho — async twin of test_sangho.py.
Uses respx to mock httpx.AsyncClient calls — no real network requests.
"""

import httpx
import pytest
import respx

import sangho
from sangho import (
    AsyncSangho,
    SanghoAuthError,
    SanghoNotFoundError,
    SanghoPublicKeyError,
    SanghoRateLimitError,
    SanghoValidationError,
)

BASE = "https://api.sangho.ga/v1"


@pytest.fixture
def client():
    return AsyncSangho("sk_test_abc123456789")


# ---------------------------------------------------------------------------
# Resource wiring
# ---------------------------------------------------------------------------


def test_all_resources_wired(client):
    for name in (
        "account",
        "addresses",
        "apps",
        "customers",
        "products",
        "payment_intents",
        "payment_links",
        "checkout_sessions",
        "invoices",
        "transactions",
        "refunds",
        "subscriptions",
        "payment_methods",
        "receipts",
        "webhooks",
        "security",
        "partners",
        "terminal",
        "sandbox",
    ):
        assert hasattr(client, name)


def test_terminal_sub_resources(client):
    assert hasattr(client.terminal, "readers")
    assert hasattr(client.terminal, "sessions")
    assert hasattr(client.terminal, "offline")


# ---------------------------------------------------------------------------
# CRUD round-trips
# ---------------------------------------------------------------------------


@respx.mock
async def test_customers_list(client):
    respx.get(f"{BASE}/customers/").mock(
        return_value=httpx.Response(200, json={"count": 1, "data": [{"id": "cust_1"}]})
    )
    result = await client.customers.list()
    assert result["count"] == 1


@respx.mock
async def test_customers_retrieve(client):
    respx.get(f"{BASE}/customers/cust_1/").mock(
        return_value=httpx.Response(200, json={"id": "cust_1", "email": "a@b.com"})
    )
    customer = await client.customers.retrieve("cust_1")
    assert customer["id"] == "cust_1"


@respx.mock
async def test_payment_intent_create_and_confirm(client):
    intent = {"id": "pay_1", "status": "requires_confirmation", "amount": 5000}
    confirmed = {"id": "pay_1", "status": "succeeded", "amount": 5000}
    respx.post(f"{BASE}/payment-intents/").mock(return_value=httpx.Response(201, json=intent))
    respx.post(f"{BASE}/payment-intents/pay_1/confirm/").mock(
        return_value=httpx.Response(200, json=confirmed)
    )
    i = await client.payment_intents.create(amount=5000, customer="cust_1")
    assert i["status"] == "requires_confirmation"
    c = await client.payment_intents.confirm(i["id"])
    assert c["status"] == "succeeded"


@respx.mock
async def test_account_retrieve(client):
    respx.get(f"{BASE}/account/").mock(return_value=httpx.Response(200, json={"id": "app_1"}))
    account = await client.account.retrieve()
    assert account["id"] == "app_1"


@respx.mock
async def test_sandbox_reset(client):
    respx.post(f"{BASE}/reset/").mock(return_value=httpx.Response(204))
    result = await client.sandbox.reset()
    assert result is None


# ---------------------------------------------------------------------------
# Error mapping (same behavior as the sync client)
# ---------------------------------------------------------------------------


@respx.mock
async def test_401_raises_auth_error(client):
    respx.get(f"{BASE}/customers/").mock(
        return_value=httpx.Response(401, json={"message": "bad key"})
    )
    with pytest.raises(SanghoAuthError):
        await client.customers.list()


@respx.mock
async def test_404_raises_not_found(client):
    respx.get(f"{BASE}/customers/nope/").mock(
        return_value=httpx.Response(404, json={"message": "not found"})
    )
    with pytest.raises(SanghoNotFoundError):
        await client.customers.retrieve("nope")


@respx.mock
async def test_422_raises_validation_error(client):
    respx.post(f"{BASE}/customers/").mock(
        return_value=httpx.Response(422, json={"detail": {"email": ["This field is required."]}})
    )
    with pytest.raises(SanghoValidationError) as exc_info:
        await client.customers.create(email="", name="Test")
    assert "email" in exc_info.value.field_errors


@respx.mock
async def test_429_raises_rate_limit():
    respx.get(f"{BASE}/customers/").mock(
        return_value=httpx.Response(429, json={"message": "Rate limit", "retry_after": 30})
    )
    no_retry_client = AsyncSangho("sk_test_abc123456789", max_retries=0)
    with pytest.raises(SanghoRateLimitError) as exc_info:
        await no_retry_client.customers.list()
    assert exc_info.value.retry_after == 30


async def test_public_key_on_write():
    pub_client = AsyncSangho("pk_test_abc123456789")
    with pytest.raises(SanghoPublicKeyError):
        await pub_client.customers.list()


def test_invalid_key_prefix():
    with pytest.raises(ValueError):
        AsyncSangho("bad_key_without_prefix")


# ---------------------------------------------------------------------------
# sangho.error aliases resolve to the same exceptions as the sync client
# ---------------------------------------------------------------------------


@respx.mock
async def test_error_aliases_catch_same_exception(client):
    respx.get(f"{BASE}/customers/").mock(
        return_value=httpx.Response(401, json={"message": "bad key"})
    )
    with pytest.raises(sangho.error.AuthenticationError):
        await client.customers.list()


# ---------------------------------------------------------------------------
# Async context manager
# ---------------------------------------------------------------------------


async def test_async_context_manager():
    async with AsyncSangho("sk_test_abc123456789") as c:
        assert c._client is not None
