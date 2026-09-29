"""Signature des webhooks (spéc. SDK-06 / PY-05) : erreurs typées, rotation, tolérance, corps brut."""

import hashlib
import hmac
import json
import time

import pytest

from sangho import Sangho, SanghoError, SanghoWebhookSignatureError
from sangho.resources.webhooks import Webhooks

SECRET = "whsec_test_secret"
ACCOUNT = {
    "id": "acct_" + "b" * 32,
    "object": "account",
    "status": "active",
    "charges_enabled": True,
    "kyc_level": 1,
}
BODY = json.dumps(
    {"id": "evt_1", "type": "kyc.updated", "created": 1780000100, "data": {"object": ACCOUNT}}
).encode()


def sign(secret: str, ts: int, payload: bytes) -> str:
    return hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()


def reason_of(
    header: str, payload: bytes = BODY, secret=SECRET, **kwargs
) -> SanghoWebhookSignatureError:
    with pytest.raises(SanghoWebhookSignatureError) as info:
        Webhooks.construct_event(payload, header, secret, **kwargs)
    return info.value


def test_signature_valide_retourne_l_evenement_kyc():
    ts = int(time.time())
    event = Webhooks.construct_event(BODY, f"t={ts},v1={sign(SECRET, ts, BODY)}", SECRET)
    assert event["type"] == "kyc.updated"
    assert event["data"]["object"]["charges_enabled"] is True


def test_exposee_sur_le_client_et_generate_test_header():
    header = Sangho.generate_test_header(BODY, SECRET)
    assert Sangho.construct_event(BODY, header, SECRET)["type"] == "kyc.updated"


def test_corps_utf8_et_str():
    payload = json.dumps(
        {"type": "account.updated", "data": {"object": {"business_name": "Café Épicé"}}},
        ensure_ascii=False,
    )
    header = Webhooks.generate_test_header(payload, SECRET)
    assert Webhooks.construct_event(payload, header, SECRET)["type"] == "account.updated"


def test_corps_altere_mismatch_401():
    ts = int(time.time())
    error = reason_of(f"t={ts},v1={sign(SECRET, ts, BODY)}", payload=BODY + b" ")
    assert (error.reason, error.status_code) == ("mismatch", 401)


def test_mauvais_secret_mismatch():
    ts = int(time.time())
    assert reason_of(f"t={ts},v1={sign('autre', ts, BODY)}").reason == "mismatch"


def test_horodatage_expire_ou_futur_expired_400():
    for ts in (int(time.time()) - 3600, int(time.time()) + 3600):
        error = reason_of(f"t={ts},v1={sign(SECRET, ts, BODY)}")
        assert (error.reason, error.status_code, error.code) == ("expired", 400, "stale_event")


def test_tolerance_personnalisee():
    ts = int(time.time()) - 600
    header = f"t={ts},v1={sign(SECRET, ts, BODY)}"
    reason_of(header)
    assert Webhooks.construct_event(BODY, header, SECRET, tolerance=900)["type"] == "kyc.updated"


@pytest.mark.parametrize(
    "header", ["", "nimportequoi", "t=abc,v1=deadbeef", "t=123", "v1=deadbeef", "t=,v1="]
)
def test_en_tete_mal_forme(header):
    assert reason_of(header).reason == "malformed"


def test_rotation_plusieurs_v1_dans_l_en_tete():
    ts = int(time.time())
    header = f"t={ts},v1={sign('ancien-secret', ts, BODY)},v1={sign(SECRET, ts, BODY)}"
    assert Webhooks.construct_event(BODY, header, SECRET)["type"] == "kyc.updated"


def test_rotation_plusieurs_secrets():
    ts = int(time.time())
    header = f"t={ts},v1={sign('ancien-secret', ts, BODY)}"
    assert (
        Webhooks.construct_event(BODY, header, [SECRET, "ancien-secret"])["type"] == "kyc.updated"
    )
    assert reason_of(header, secret=[SECRET]).reason == "mismatch"


def test_corps_non_json_signature_pourtant_valide():
    ts = int(time.time())
    raw = b"pas du json"
    with pytest.raises(SanghoError, match="valid JSON"):
        Webhooks.construct_event(raw, f"t={ts},v1={sign(SECRET, ts, raw)}", SECRET)


def test_sous_classe_de_sangho_error_pour_la_compatibilite():
    assert issubclass(SanghoWebhookSignatureError, SanghoError)
