"""Tests for webhook signature verification."""
import hashlib
import hmac
import json
import time

import pytest

from sangho.resources.webhooks import Webhooks
from sangho._errors import SanghoError


def _make_header(payload: bytes, secret: str, timestamp: int | None = None) -> str:
    ts = timestamp or int(time.time())
    signed = f"{ts}.".encode() + payload
    sig = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


def test_valid_signature():
    secret = "whsec_test_secret"
    payload = json.dumps({"event": "payment_intent.succeeded"}).encode()
    header = _make_header(payload, secret)
    event = Webhooks.construct_event(payload, header, secret)
    assert event["event"] == "payment_intent.succeeded"


def test_invalid_signature():
    payload = b'{"event": "test"}'
    header = _make_header(payload, "correct_secret")
    with pytest.raises(SanghoError, match="signature mismatch"):
        Webhooks.construct_event(payload, header, "wrong_secret")


def test_stale_timestamp():
    secret = "whsec_test_secret"
    payload = b'{"event": "test"}'
    old_ts = int(time.time()) - 600  # 10 minutes ago
    header = _make_header(payload, secret, timestamp=old_ts)
    with pytest.raises(SanghoError, match="too old"):
        Webhooks.construct_event(payload, header, secret, tolerance=300)
