from __future__ import annotations

import builtins
import hashlib
import hmac
import json
import time

from sangho._base import BaseResource
from sangho._errors import SanghoError, SanghoWebhookSignatureError


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
        secret: str | builtins.list[str],
        tolerance: int = 300,
    ) -> dict:
        """Vérifie la signature HMAC-SHA256 et retourne l'événement (dict).

        ``Sangho-Signature: t=<ts>,v1=<hex>[,v1=<hex>…]`` ; message signé ``"<ts>.<corps brut>"``. Plusieurs ``v1``
        (et une liste de secrets) sont acceptés pour la rotation ; comparaison à temps constant. Lève
        `SanghoWebhookSignatureError` (``reason`` : ``malformed`` / ``expired`` / ``mismatch``), sous-classe de
        `SanghoError`. Le corps doit être le corps BRUT (octets) reçu.
        """
        if isinstance(payload, str):
            payload = payload.encode()

        timestamp, signatures = Webhooks._parse_header(signature_header)

        if abs(time.time() - timestamp) > tolerance:
            raise SanghoWebhookSignatureError("expired", "Webhook timestamp too old.")

        signed_payload = f"{timestamp}.".encode() + payload
        secrets = [secret] if isinstance(secret, str) else list(secret)
        matched = False
        for candidate in secrets:
            if not candidate:
                continue
            expected = hmac.new(candidate.encode(), signed_payload, hashlib.sha256).hexdigest()
            for (
                received
            ) in signatures:  # pas de court-circuit : temps indépendant du v1 correspondant
                if hmac.compare_digest(expected, received):
                    matched = True
        if not matched:
            raise SanghoWebhookSignatureError("mismatch", "Webhook signature mismatch.")

        try:
            return json.loads(payload)
        except ValueError:
            raise SanghoError(
                "Webhook body is not valid JSON.", code="invalid_payload", status_code=400
            ) from None

    @staticmethod
    def _parse_header(header: str) -> tuple[int, builtins.list[str]]:
        malformed = SanghoWebhookSignatureError("malformed", "Invalid Sangho-Signature header.")
        if not isinstance(header, str) or not header:
            raise malformed
        timestamp: int | None = None
        signatures: builtins.list[str] = []
        for part in header.split(","):
            key, sep, value = part.partition("=")
            if not sep:
                continue
            key, value = key.strip(), value.strip()
            if key == "t":
                if not value.isdigit():
                    raise malformed
                timestamp = int(value)
            elif key == "v1" and value:
                signatures.append(value)
        if timestamp is None or not signatures:
            raise malformed
        return timestamp, signatures

    @staticmethod
    def generate_test_header(
        payload: str | bytes, secret: str, timestamp: int | None = None
    ) -> str:
        """Génère un en-tête ``Sangho-Signature`` valide pour tester votre endpoint."""
        if isinstance(payload, str):
            payload = payload.encode()
        ts = int(time.time()) if timestamp is None else int(timestamp)
        digest = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
        return f"t={ts},v1={digest}"
