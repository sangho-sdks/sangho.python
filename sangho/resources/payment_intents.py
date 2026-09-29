from __future__ import annotations

from sangho._base import BaseResource


class PaymentIntents(BaseResource):
    _path = "/payment-intents/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("payment_intents.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("payment_intents.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(
        self,
        amount: int | float | str,
        currency: str = "XAF",
        customer_email: str | None = None,
        *,
        idempotency_key: str | None = None,
        **opts,
    ) -> dict:
        """
        Args:
            amount: Montant en unité MAJEURE de la devise (5000 = 5000 XAF), jamais en centimes.
            currency: Code ISO 4217 (défaut ``XAF``) — exigé par le backend.
            customer_email: E-mail de l'acheteur (le backend lit ``customer_email``, pas ``customer``).
            idempotency_key: rejoue l'appel sans doublon (même clé + même corps = même réponse).
            description, metadata, category, payment_method_types: optionnels.
        """
        self._client.assert_secret_key("payment_intents.create")
        body = {"amount": amount, "currency": currency, **opts}
        if customer_email:
            body["customer_email"] = customer_email
        return self._client.post(self._path, body=body, idempotency_key=idempotency_key)

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("payment_intents.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def confirm(self, id: str, **payloads) -> dict:
        """Confirm a payment intent."""
        self._client.assert_secret_key("payment_intents.confirm")
        return self._client.post(f"{self._path}{id}/confirm/", body=payloads)

    def capture(self, id: str, **payloads) -> dict:
        """Capture an authorized payment intent."""
        self._client.assert_secret_key("payment_intents.capture")
        return self._client.post(f"{self._path}{id}/capture/", body=payloads)

    def cancel(self, id: str, **payloads) -> dict:
        """Cancel a payment intent."""
        self._client.assert_secret_key("payment_intents.cancel")
        return self._client.post(f"{self._path}{id}/cancel/", body=payloads)

    def options(self) -> dict:
        return self._client.options(self._path)
