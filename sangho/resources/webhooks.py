from __future__ import annotations

import builtins
import hashlib
import hmac
import json
import time

from sangho._base import BaseResource
from sangho._errors import SanghoError


class Webhooks(BaseResource):
    _path = "/webhooks/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("webhooks.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("webhooks.retrieve")
        return self._client.get(f"{self._path}{id}/")

    # `builtins.list` plutôt que `list` : cette classe déclare sa propre
    # méthode `list` ci-dessus, qui masque le type builtin `list` dans
    # l'espace de noms de la classe pour la résolution des annotations
    # différées (from __future__ import annotations) — sans ce préfixe,
    # mypy résout `list[str]` vers `Webhooks.list` et non vers le builtin.
    def create(self, url: str, events: builtins.list[str], **opts) -> dict:
        self._client.assert_secret_key("webhooks.create")
        return self._client.post(self._path, body={"url": url, "events": events, **opts})

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("webhooks.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def delete(self, id: str) -> None:
        self._client.assert_secret_key("webhooks.delete")
        return self._client.delete(f"{self._path}{id}/")

    def roll_secret(self, id: str) -> dict:
        self._client.assert_secret_key("webhooks.roll_secret")
        return self._client.post(f"{self._path}{id}/roll-secret/")

    def send_test_event(self, id: str, event_type: str) -> dict:
        self._client.assert_secret_key("webhooks.send_test_event")
        return self._client.post(f"{self._path}{id}/test/", body={"event_type": event_type})

    def list_deliveries(self, id: str, **criteria) -> dict:
        self._client.assert_secret_key("webhooks.list_deliveries")
        return self._client.get(f"{self._path}{id}/deliveries/", params=criteria or None)

    def disable(self, id: str) -> dict:
        self._client.assert_secret_key("webhooks.disable")
        return self._client.post(f"{self._path}{id}/disable/")

    def enable(self, id: str) -> dict:
        self._client.assert_secret_key("webhooks.enable")
        return self._client.post(f"{self._path}{id}/enable/")

    def retrieve_delivery(self, id: str, delivery_id: str) -> dict:
        self._client.assert_secret_key("webhooks.retrieve_delivery")
        return self._client.get(f"{self._path}{id}/deliveries/{delivery_id}/")

    def retry_delivery(self, id: str, delivery_id: str) -> dict:
        self._client.assert_secret_key("webhooks.retry_delivery")
        return self._client.post(f"{self._path}{id}/deliveries/{delivery_id}/retry/")

    def options(self) -> dict:
        return self._client.options(self._path)

    @staticmethod
    def construct_event(
        payload: str | bytes,
        signature_header: str,
        secret: str,
        tolerance: int = 300,
    ) -> dict:
        """Verify HMAC-SHA256 signature and return parsed event dict."""
        if isinstance(payload, str):
            payload = payload.encode()

        parts = dict(p.split("=", 1) for p in signature_header.split(",") if "=" in p)
        timestamp = parts.get("t")
        received_sig = parts.get("v1")

        if not timestamp or not received_sig:
            raise SanghoError("Invalid Sangho-Signature header.", code="invalid_signature")

        if abs(time.time() - int(timestamp)) > tolerance:
            raise SanghoError("Webhook timestamp too old.", code="stale_event")

        signed_payload = f"{timestamp}.".encode() + payload
        expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected, received_sig):
            raise SanghoError("Webhook signature mismatch.", code="invalid_signature")

        return json.loads(payload)
