"""Marketplace / Connect, clé d'idempotence (PY-04), corps de paiement (PY-01/02) et non-rejeu d'un POST (PY-03)."""

import json

import httpx
import pytest
import respx

from sangho import (
    AsyncSangho,
    Sangho,
    SanghoConflictError,
    SanghoIdempotencyError,
    SanghoNotFoundError,
    SanghoPublicKeyError,
    SanghoTimeoutError,
    SanghoValidationError,
)

BASE = "https://api.sangho.ga/v1"
ACCOUNT_ID = "acct_" + "a" * 32
ACCOUNT = {
    "id": ACCOUNT_ID, "object": "account", "external_id": "seller-1", "email": "ada@example.com",
    "business_name": "Boutique Ada", "status": "pending_claim", "charges_enabled": False,
    "payouts_enabled": False, "kyc_level": 0, "livemode": False, "created": 1780000000,
}


@pytest.fixture
def client():
    return Sangho("sk_test_abc123456789", max_retries=2)


def body_of(route) -> dict:
    return json.loads(route.calls.last.request.content)


# ── comptes Connect ──────────────────────────────────────────────────────────────────────────────
@respx.mock
def test_create_account_envoie_le_corps_et_retourne_le_claim_token(client):
    route = respx.post(f"{BASE}/connect/accounts/").mock(
        return_value=httpx.Response(201, json={**ACCOUNT, "claim_token": "tok_xxx"})
    )
    account = client.connect.accounts.create("seller-1", "ada@example.com", "Boutique Ada")
    assert body_of(route) == {
        "external_id": "seller-1", "email": "ada@example.com", "business_name": "Boutique Ada", "phone": "",
    }
    assert account["claim_token"] == "tok_xxx"


@respx.mock
def test_create_account_cle_d_idempotence_fournie(client):
    route = respx.post(f"{BASE}/connect/accounts/").mock(return_value=httpx.Response(200, json=ACCOUNT))
    client.connect.accounts.create("seller-1", "ada@example.com", idempotency_key="connect-account-seller-1")
    request = route.calls.last.request
    assert request.headers["Idempotency-Key"] == "connect-account-seller-1"
    assert "idempotency_key" not in json.loads(request.content)


@respx.mock
def test_retrieve_list_reissue(client):
    respx.get(f"{BASE}/connect/accounts/{ACCOUNT_ID}/").mock(
        return_value=httpx.Response(200, json={**ACCOUNT, "status": "active", "charges_enabled": True, "kyc_level": 1})
    )
    respx.get(f"{BASE}/connect/accounts/").mock(return_value=httpx.Response(200, json={"object": "list", "data": [ACCOUNT]}))
    reissue = respx.post(f"{BASE}/connect/accounts/{ACCOUNT_ID}/claim-token/").mock(
        return_value=httpx.Response(200, json={"id": ACCOUNT_ID, "claim_token": "tok_new"})
    )
    assert client.connect.accounts.retrieve(ACCOUNT_ID)["charges_enabled"] is True
    assert len(client.connect.accounts.list()["data"]) == 1
    assert client.connect.accounts.reissue_claim_token(ACCOUNT_ID)["claim_token"] == "tok_new"
    assert reissue.called


@respx.mock
def test_create_kyc_session(client):
    session = {
        "object": "kyc_session", "url": "https://dash.sangho.ga/connect/kyc/?session=abc",
        "expires_at": 1780003600, "account": ACCOUNT_ID,
    }
    route = respx.post(f"{BASE}/connect/accounts/{ACCOUNT_ID}/kyc-session/").mock(return_value=httpx.Response(201, json=session))
    result = client.connect.accounts.create_kyc_session(ACCOUNT_ID, "https://evangzat.com/wallet/", "https://evangzat.com/wallet/")
    assert body_of(route) == {"return_url": "https://evangzat.com/wallet/", "refresh_url": "https://evangzat.com/wallet/"}
    assert result["url"].startswith("https://dash.sangho.ga/connect/kyc/")


@respx.mock
def test_kyc_session_compte_non_reclame_conflit_metier(client):
    respx.post(f"{BASE}/connect/accounts/{ACCOUNT_ID}/kyc-session/").mock(
        return_value=httpx.Response(409, json={"error": {"code": "account_not_claimed", "message": "Compte non réclamé."}})
    )
    with pytest.raises(SanghoConflictError) as info:
        client.connect.accounts.create_kyc_session(ACCOUNT_ID, "https://evangzat.com/wallet/")
    assert info.value.code == "account_not_claimed"
    assert info.value.status_code == 409
    assert not isinstance(info.value, SanghoIdempotencyError)


@respx.mock
def test_erreurs_404_et_422_du_format_imbrique(client):
    respx.post(f"{BASE}/connect/accounts/{ACCOUNT_ID}/kyc-session/").mock(
        return_value=httpx.Response(404, json={"error": {"code": "resource_missing", "message": "Compte introuvable."}})
    )
    with pytest.raises(SanghoNotFoundError):
        client.connect.accounts.create_kyc_session(ACCOUNT_ID, "https://x.y/")
    respx.post(f"{BASE}/connect/accounts/{ACCOUNT_ID}/kyc-session/").mock(
        return_value=httpx.Response(422, json={"code": "invalid_url", "message": "https requis"})
    )
    with pytest.raises(SanghoValidationError):
        client.connect.accounts.create_kyc_session(ACCOUNT_ID, "http://x.y/")


@respx.mock
def test_409_sans_code_reste_une_erreur_d_idempotence(client):
    respx.post(f"{BASE}/connect/accounts/").mock(return_value=httpx.Response(409, json={"message": "Conflict"}))
    with pytest.raises(SanghoIdempotencyError):
        client.connect.accounts.create("seller-1", "ada@example.com")


def test_cle_publique_refusee():
    pub = Sangho("pk_test_abc123456789")
    with pytest.raises(SanghoPublicKeyError):
        pub.connect.accounts.list()
    with pytest.raises(SanghoPublicKeyError):
        pub.connect.accounts.create_kyc_session(ACCOUNT_ID, "https://x.y/")


@respx.mock
async def test_version_asynchrone():
    route = respx.post(f"{BASE}/connect/accounts/{ACCOUNT_ID}/kyc-session/").mock(
        return_value=httpx.Response(201, json={"object": "kyc_session", "url": "https://dash.sangho.ga/x", "expires_at": 1, "account": ACCOUNT_ID})
    )
    respx.post(f"{BASE}/connect/accounts/").mock(return_value=httpx.Response(201, json=ACCOUNT))
    async with AsyncSangho("sk_test_abc123456789") as async_client:
        created = await async_client.connect.accounts.create("seller-1", "ada@example.com", idempotency_key="k1")
        session = await async_client.connect.accounts.create_kyc_session(ACCOUNT_ID, "https://evangzat.com/wallet/")
    assert created["id"] == ACCOUNT_ID
    assert session["url"] == "https://dash.sangho.ga/x"
    assert route.called


# ── PY-01 / PY-02 : corps conformes au backend ───────────────────────────────────────────────────
@respx.mock
def test_payment_intent_envoie_la_devise_et_customer_email(client):
    route = respx.post(f"{BASE}/payment-intents/").mock(return_value=httpx.Response(201, json={"id": "pi_1"}))
    client.payment_intents.create(5000, "XAF", "ada@example.com", idempotency_key="order-42")
    request = route.calls.last.request
    assert json.loads(request.content) == {"amount": 5000, "currency": "XAF", "customer_email": "ada@example.com"}
    assert request.headers["Idempotency-Key"] == "order-42"


@respx.mock
def test_payment_intent_devise_par_defaut_xaf(client):
    route = respx.post(f"{BASE}/payment-intents/").mock(return_value=httpx.Response(201, json={"id": "pi_1"}))
    client.payment_intents.create(amount=5000)
    assert body_of(route)["currency"] == "XAF"


@respx.mock
def test_checkout_session_envoie_line_items(client):
    route = respx.post(f"{BASE}/checkout-sessions/").mock(return_value=httpx.Response(201, json={"id": "cs_1"}))
    items = [{"name": "Robe", "unit_amount": 5000, "quantity": 2}]
    client.checkout_sessions.create(items, "https://evangzat.com/ok/", "https://evangzat.com/ko/", idempotency_key="cs-42")
    assert body_of(route) == {
        "line_items": items, "success_url": "https://evangzat.com/ok/", "currency": "XAF", "cancel_url": "https://evangzat.com/ko/",
    }
    assert route.calls.last.request.headers["Idempotency-Key"] == "cs-42"


@respx.mock
def test_checkout_session_ancienne_signature_convertie_avec_avertissement(client):
    route = respx.post(f"{BASE}/checkout-sessions/").mock(return_value=httpx.Response(201, json={"id": "cs_1"}))
    with pytest.warns(DeprecationWarning):
        client.checkout_sessions.create(5000, "https://evangzat.com/ok/", "https://evangzat.com/ko/")
    assert body_of(route)["line_items"] == [{"name": "Paiement", "unit_amount": 5000, "quantity": 1}]


# ── PY-03 : pas de rejeu aveugle d'un POST après un timeout ──────────────────────────────────────
@respx.mock
def test_post_non_rejoue_apres_timeout_sans_cle_fournie(client, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _s: None)
    route = respx.post(f"{BASE}/checkout-sessions/").mock(side_effect=httpx.ReadTimeout("lent"))
    with pytest.raises(SanghoTimeoutError):
        client.checkout_sessions.create([{"name": "x", "unit_amount": 1}], "https://a.b/")
    assert route.call_count == 1


@respx.mock
def test_post_rejoue_apres_timeout_avec_cle_fournie(client, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _s: None)
    route = respx.post(f"{BASE}/checkout-sessions/").mock(side_effect=httpx.ReadTimeout("lent"))
    with pytest.raises(SanghoTimeoutError):
        client.checkout_sessions.create([{"name": "x", "unit_amount": 1}], "https://a.b/", idempotency_key="k")
    assert route.call_count == 3      # 1 essai + 2 rejeux : la clé rend le rejeu sûr


@respx.mock
def test_get_toujours_rejoue_apres_timeout(client, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _s: None)
    route = respx.get(f"{BASE}/connect/accounts/").mock(side_effect=httpx.ReadTimeout("lent"))
    with pytest.raises(SanghoTimeoutError):
        client.connect.accounts.list()
    assert route.call_count == 3
