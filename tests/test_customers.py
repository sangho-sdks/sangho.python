"""Tests for the Customers resource."""
import pytest
import respx
import httpx

from sangho import Sangho, SanghoNotFoundError, SanghoValidationError, SanghoPublicKeyError

BASE = "https://api.sangho.com/v1"


@pytest.fixture
def client():
    return Sangho("sk_test_abc123456789")


@respx.mock
def test_list_customers(client):
    respx.get(f"{BASE}/customers/").mock(
        return_value=httpx.Response(200, json={"count": 1, "next": None, "previous": None,
                                               "results": [{"id": "cust_1", "email": "a@b.com"}]})
    )
    result = client.customers.list()
    assert result["count"] == 1
    assert result["results"][0]["email"] == "a@b.com"


@respx.mock
def test_retrieve_customer(client):
    respx.get(f"{BASE}/customers/cust_1/").mock(
        return_value=httpx.Response(200, json={"id": "cust_1", "email": "a@b.com"})
    )
    customer = client.customers.retrieve("cust_1")
    assert customer["id"] == "cust_1"


@respx.mock
def test_create_customer(client):
    respx.post(f"{BASE}/customers/").mock(
        return_value=httpx.Response(201, json={"id": "cust_new", "email": "jean@example.com"})
    )
    customer = client.customers.create(email="jean@example.com", name="Jean Ondo")
    assert customer["id"] == "cust_new"


@respx.mock
def test_not_found(client):
    respx.get(f"{BASE}/customers/cust_bad/").mock(
        return_value=httpx.Response(404, json={"message": "Not found"})
    )
    with pytest.raises(SanghoNotFoundError):
        client.customers.retrieve("cust_bad")


@respx.mock
def test_validation_error(client):
    respx.post(f"{BASE}/customers/").mock(
        return_value=httpx.Response(422, json={
            "message": "Validation error",
            "detail": {"email": ["Enter a valid email address."]}
        })
    )
    with pytest.raises(SanghoValidationError) as exc_info:
        client.customers.create(email="bad-email", name="Jean")
    assert "email" in exc_info.value.field_errors


def test_public_key_raises():
    pub_client = Sangho("pk_test_abc123456789")
    with pytest.raises(SanghoPublicKeyError):
        pub_client.customers.list()


@respx.mock
def test_delete_customer(client):
    respx.delete(f"{BASE}/customers/cust_1/").mock(
        return_value=httpx.Response(204)
    )
    result = client.customers.delete("cust_1")
    assert result is None
