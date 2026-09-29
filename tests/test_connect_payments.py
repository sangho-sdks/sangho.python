"""Paiements Connect (séquestre) : release / refund / freeze, soldes et retraits — sync et async, sans réseau."""

import json

import httpx
import pytest
import respx

from sangho import AsyncSangho, Sangho, SanghoPublicKeyError, SanghoValidationError

BASE = "https://api.sangho.ga/v1"
PAY = "cpay_" + "b" * 32
ACCT = "acct_" + "a" * 32


@pytest.fixture
def client():
    return Sangho("sk_test_abc123456789", max_retries=1)


def body_of(route) -> dict:
    return json.loads(route.calls.last.request.content)


@respx.mock
def test_retrieve_payment(client):
    respx.get(f"{BASE}/connect/payments/{PAY}/").mock(return_value=httpx.Response(200, json={"id": PAY, "status": "held"}))
    assert client.connect.payments.retrieve(PAY)["status"] == "held"


@respx.mock
def test_release_envoie_la_cle_d_idempotence(client):
    route = respx.post(f"{BASE}/connect/payments/{PAY}/release/").mock(return_value=httpx.Response(200, json={"status": "released"}))
    client.connect.payments.release(PAY, idempotency_key="release-ORDER-1")
    assert route.calls.last.request.headers["Idempotency-Key"] == "release-ORDER-1"


def test_release_sans_cle_refuse_sans_appel_reseau(client):
    with pytest.raises(SanghoValidationError):
        client.connect.payments.release(PAY, idempotency_key="")


@respx.mock
def test_refund_scope_et_montant(client):
    route = respx.post(f"{BASE}/connect/payments/{PAY}/refund/").mock(return_value=httpx.Response(200, json={"status": "partially_refunded"}))
    client.connect.payments.refund(PAY, "amount", amount=1500, reason="geste", idempotency_key="refund-1")
    assert body_of(route) == {"scope": "amount", "amount": 1500, "reason": "geste"}


def test_refund_scope_invalide(client):
    with pytest.raises(SanghoValidationError):
        client.connect.payments.refund(PAY, "tout", idempotency_key="refund-1")


@respx.mock
def test_freeze_et_unfreeze(client):
    freeze = respx.post(f"{BASE}/connect/payments/{PAY}/freeze/").mock(return_value=httpx.Response(200, json={"status": "frozen"}))
    unfreeze = respx.post(f"{BASE}/connect/payments/{PAY}/unfreeze/").mock(return_value=httpx.Response(200, json={"status": "held"}))
    assert client.connect.payments.freeze(PAY)["status"] == "frozen"
    assert client.connect.payments.unfreeze(PAY)["status"] == "held"
    assert freeze.called and unfreeze.called


@respx.mock
def test_simulate_payment(client):
    route = respx.post(f"{BASE}/connect/payments/{PAY}/simulate-payment/").mock(return_value=httpx.Response(200, json={"status": "held"}))
    client.connect.payments.simulate_payment(PAY)
    assert route.called


@respx.mock
def test_balance_et_payouts(client):
    respx.get(f"{BASE}/connect/accounts/{ACCT}/balance/").mock(return_value=httpx.Response(200, json={"available": "2000.00", "held": "25000.00"}))
    payout = respx.post(f"{BASE}/connect/accounts/{ACCT}/payouts/").mock(return_value=httpx.Response(201, json={"id": "cpo_x", "status": "pending"}))
    respx.get(f"{BASE}/connect/accounts/{ACCT}/payouts/").mock(return_value=httpx.Response(200, json={"object": "list", "data": []}))
    assert client.connect.accounts.balance(ACCT)["held"] == "25000.00"
    client.connect.accounts.create_payout(ACCT, 1000, "mobile:077000000", idempotency_key="payout-1")
    assert body_of(payout) == {"amount": 1000, "destination": "mobile:077000000"}
    assert client.connect.accounts.list_payouts(ACCT)["data"] == []


def test_cle_publique_refusee():
    public = Sangho("pk_test_abc123456789")
    with pytest.raises(SanghoPublicKeyError):
        public.connect.payments.retrieve(PAY)


@pytest.mark.asyncio
@respx.mock
async def test_async_release_et_balance():
    route = respx.post(f"{BASE}/connect/payments/{PAY}/release/").mock(return_value=httpx.Response(200, json={"status": "released"}))
    respx.get(f"{BASE}/connect/accounts/{ACCT}/balance/").mock(return_value=httpx.Response(200, json={"available": "1.00"}))
    async with AsyncSangho("sk_test_abc123456789") as client:
        await client.connect.payments.release(PAY, idempotency_key="release-async")
        assert (await client.connect.accounts.balance(ACCT))["available"] == "1.00"
        with pytest.raises(SanghoValidationError):
            await client.connect.payments.release(PAY, idempotency_key="")
    assert route.calls.last.request.headers["Idempotency-Key"] == "release-async"
