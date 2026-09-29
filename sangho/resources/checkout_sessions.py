from __future__ import annotations

import warnings

from sangho._base import BaseResource


class CheckoutSessions(BaseResource):
    _path = "/checkout-sessions/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("checkout_sessions.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        # Le backend autorise explicitement la clé publique sur cette action
        # (page de confirmation côté navigateur) — ne pas la bloquer ici.
        return self._client.get(f"{self._path}{id}/")

    def create(
        self,
        line_items: list[dict] | int | float,
        success_url: str,
        cancel_url: str | None = None,
        *,
        currency: str = "XAF",
        idempotency_key: str | None = None,
        **opts,
    ) -> dict:
        """
        Args:
            line_items: Lignes du panier ; ``product`` est facultatif, sinon ``name`` et ``unit_amount``
                (unité majeure) sont requis, ex. ``[{"name": "Robe", "unit_amount": 5000, "quantity": 1}]``.
                Un montant seul (ancienne signature) est converti en une ligne ad hoc.
            success_url: Redirect URL on success (le backend l'exige).
            cancel_url: Redirect URL on cancel.
            currency: Code ISO 4217 (défaut ``XAF``).
            idempotency_key: rejoue l'appel sans doublon.
        """
        self._client.assert_secret_key("checkout_sessions.create")
        if isinstance(line_items, (int, float)):
            warnings.warn(
                "checkout_sessions.create(amount, …) est obsolète : passez `line_items`.",
                DeprecationWarning,
                stacklevel=2,
            )
            line_items = [{"name": "Paiement", "unit_amount": line_items, "quantity": 1}]
        body = {"line_items": line_items, "success_url": success_url, "currency": currency, **opts}
        if cancel_url:
            body["cancel_url"] = cancel_url
        return self._client.post(self._path, body=body, idempotency_key=idempotency_key)

    def expire(self, id: str) -> dict:
        self._client.assert_secret_key("checkout_sessions.expire")
        return self._client.post(f"{self._path}{id}/expire/")

    def delete(self, id: str) -> dict:
        self._client.assert_secret_key("checkout_sessions.delete")
        return self._client.delete(f"{self._path}{id}/")

    def options(self) -> dict:
        return self._client.options(self._path)
