"""Tests d'intégration — Webhooks (CRUD + signature)"""
import hashlib
import hmac
import json
import time
import uuid
import pytest
from sangho import SanghoNotFoundError
from sangho.resources.webhooks import Webhooks

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def test_webhook(client):
    webhook = client.webhooks.create(
        url="https://webhook.site/" + uuid.uuid4().hex,
        events=["payment_intent.succeeded", "customer.created"],
    )
    yield webhook
    try:
        client.webhooks.delete(webhook["id"])
    except Exception:
        pass


class TestWebhooksIntegration:

    def test_create_webhook(self, client):
        wh = client.webhooks.create(
            url="https://webhook.site/" + uuid.uuid4().hex,
            events=["payment_intent.succeeded"],
        )
        assert wh["id"]
        assert wh["url"]
        assert "payment_intent.succeeded" in wh.get("events", [])
        client.webhooks.delete(wh["id"])

    def test_retrieve_webhook(self, client, test_webhook):
        retrieved = client.webhooks.retrieve(test_webhook["id"])
        assert retrieved["id"] == test_webhook["id"]

    def test_list_webhooks(self, client):
        result = client.webhooks.list()
        assert "results" in result

    def test_update_webhook(self, client, test_webhook):
        updated = client.webhooks.update(
            test_webhook["id"],
            events=["payment_intent.succeeded", "refund.created"],
        )
        assert "refund.created" in updated.get("events", [])

    def test_roll_secret(self, client, test_webhook):
        result = client.webhooks.roll_secret(test_webhook["id"])
        assert result["id"] == test_webhook["id"]

    def test_list_deliveries(self, client, test_webhook):
        result = client.webhooks.list_deliveries(test_webhook["id"])
        assert "results" in result

    def test_delete_nonexistent_raises(self, client):
        with pytest.raises(SanghoNotFoundError):
            client.webhooks.retrieve("wh_doesnotexist000")

    # ── Vérification de signature (hors réseau) ───────────────────────────────

    def test_construct_event_valid_signature(self):
        secret  = "whsec_test_integration_secret"
        payload = json.dumps({"event": "payment_intent.succeeded", "id": "pay_xxx"})
        ts      = int(time.time())
        signed  = f"{ts}.".encode() + payload.encode()
        sig     = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        header  = f"t={ts},v1={sig}"

        event = Webhooks.construct_event(payload, header, secret)
        assert event["event"] == "payment_intent.succeeded"

    def test_construct_event_wrong_secret_raises(self):
        from sangho._errors import SanghoError
        secret  = "whsec_correct"
        payload = b'{"event":"test"}'
        ts      = int(time.time())
        signed  = f"{ts}.".encode() + payload
        sig     = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        header  = f"t={ts},v1={sig}"

        with pytest.raises(SanghoError, match="mismatch"):
            Webhooks.construct_event(payload, header, "whsec_wrong")

    def test_construct_event_stale_timestamp_raises(self):
        from sangho._errors import SanghoError
        secret  = "whsec_test"
        payload = b'{"event":"test"}'
        old_ts  = int(time.time()) - 600
        signed  = f"{old_ts}.".encode() + payload
        sig     = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        header  = f"t={old_ts},v1={sig}"

        with pytest.raises(SanghoError, match="old"):
            Webhooks.construct_event(payload, header, secret, tolerance=300)
