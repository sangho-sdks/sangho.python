"""Marketplace / Connect (version asynchrone) : comptes des vendeurs et KYC hébergé par Sangho.

Réservé aux Apps ayant le statut **Partenaire Plateforme** — voir ``sangho.resources.connect``
(version synchrone) pour le détail ; une App marchande ordinaire (B2C) reçoit un 403
``sangho.SanghoPlatformPartnerRequiredError``.
"""

from __future__ import annotations

from sangho._base_async import AsyncBaseResource
from sangho._errors import SanghoValidationError
from sangho.resources.connect import _require_key


class ConnectAccounts(AsyncBaseResource):
    """``client.connect.accounts`` — mêmes méthodes que la version synchrone (voir `sangho.resources.connect`)."""

    _path = "/connect/accounts/"

    async def create(
        self,
        external_id: str,
        email: str,
        business_name: str = "",
        phone: str = "",
        *,
        idempotency_key: str | None = None,
    ) -> dict:
        self._client.assert_secret_key("connect.accounts.create")
        body = {
            "external_id": str(external_id),
            "email": email,
            "business_name": business_name,
            "phone": phone,
        }
        return await self._client.post(self._path, body=body, idempotency_key=idempotency_key)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("connect.accounts.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def list(self) -> dict:
        self._client.assert_secret_key("connect.accounts.list")
        return await self._client.get(self._path)

    async def reissue_claim_token(self, id: str) -> dict:
        self._client.assert_secret_key("connect.accounts.reissue_claim_token")
        return await self._client.post(f"{self._path}{id}/claim-token/")

    async def create_kyc_session(
        self,
        id: str,
        return_url: str,
        refresh_url: str = "",
        *,
        idempotency_key: str | None = None,
    ) -> dict:
        self._client.assert_secret_key("connect.accounts.create_kyc_session")
        body = {"return_url": return_url}
        if refresh_url:
            body["refresh_url"] = refresh_url
        return await self._client.post(
            f"{self._path}{id}/kyc-session/", body=body, idempotency_key=idempotency_key
        )

    async def balance(self, id: str) -> dict:
        self._client.assert_secret_key("connect.accounts.balance")
        return await self._client.get(f"{self._path}{id}/balance/")

    async def create_payout(
        self, id: str, amount, destination: str, *, idempotency_key: str
    ) -> dict:
        self._client.assert_secret_key("connect.accounts.create_payout")
        key = _require_key("connect.accounts.create_payout", idempotency_key)
        return await self._client.post(
            f"{self._path}{id}/payouts/",
            body={"amount": amount, "destination": destination},
            idempotency_key=key,
        )

    async def list_payouts(self, id: str) -> dict:
        self._client.assert_secret_key("connect.accounts.list_payouts")
        return await self._client.get(f"{self._path}{id}/payouts/")


class ConnectPayments(AsyncBaseResource):
    """``client.connect.payments`` — mêmes méthodes que la version synchrone (voir `sangho.resources.connect`)."""

    _path = "/connect/payments/"

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("connect.payments.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def release(self, id: str, *, idempotency_key: str) -> dict:
        self._client.assert_secret_key("connect.payments.release")
        key = _require_key("connect.payments.release", idempotency_key)
        return await self._client.post(f"{self._path}{id}/release/", body={}, idempotency_key=key)

    async def refund(
        self, id: str, scope: str, amount=None, reason: str = "", *, idempotency_key: str
    ) -> dict:
        self._client.assert_secret_key("connect.payments.refund")
        key = _require_key("connect.payments.refund", idempotency_key)
        if scope not in ("product", "full", "amount"):
            raise SanghoValidationError(
                raw={"message": 'scope doit valoir "product", "full" ou "amount".'}
            )
        body: dict = {"scope": scope}
        if amount is not None:
            body["amount"] = amount
        if reason:
            body["reason"] = reason
        return await self._client.post(f"{self._path}{id}/refund/", body=body, idempotency_key=key)

    async def freeze(self, id: str, *, idempotency_key: str | None = None) -> dict:
        self._client.assert_secret_key("connect.payments.freeze")
        return await self._client.post(
            f"{self._path}{id}/freeze/", body={}, idempotency_key=idempotency_key
        )

    async def unfreeze(self, id: str, *, idempotency_key: str | None = None) -> dict:
        self._client.assert_secret_key("connect.payments.unfreeze")
        return await self._client.post(
            f"{self._path}{id}/unfreeze/", body={}, idempotency_key=idempotency_key
        )

    async def simulate_payment(self, id: str) -> dict:
        self._client.assert_secret_key("connect.payments.simulate_payment")
        return await self._client.post(f"{self._path}{id}/simulate-payment/", body={})


class Connect(AsyncBaseResource):
    def __init__(self, client) -> None:
        super().__init__(client)
        self.accounts = ConnectAccounts(client)
        self.payments = ConnectPayments(client)
