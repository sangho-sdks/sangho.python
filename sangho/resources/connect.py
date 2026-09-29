"""Marketplace / Connect : comptes des vendeurs d'une plateforme et KYC hébergé par Sangho.

Réservé aux Apps ayant le statut **Partenaire Plateforme** (approuvé manuellement par Sangho
depuis le back-office, après une demande faite sur le dashboard). Une clé secrète valide ne
suffit pas : une App marchande ordinaire (B2C) reçoit un 403
``sangho.SanghoPlatformPartnerRequiredError`` sur n'importe quel appel ci-dessous.
"""

from __future__ import annotations

from sangho._base import BaseResource
from sangho._errors import SanghoValidationError


def _require_key(method: str, idempotency_key: str | None) -> str:
    """Les écritures d'argent exigent une clé d'idempotence STABLE (ex. ``release-<commande>``) : un rejeu ne doit jamais dupliquer l'opération."""
    if not idempotency_key or not isinstance(idempotency_key, str):
        raise SanghoValidationError(
            raw={"message": f"'{method}' exige une clé d'idempotence stable (idempotency_key=…), ex : 'release-<order_id>'."}
        )
    return idempotency_key


class ConnectAccounts(BaseResource):
    """``client.connect.accounts`` — clé secrète uniquement.

    Un compte a la forme ``{"id": "acct_…", "object": "account", "external_id", "email", "business_name",
    "status", "charges_enabled", "payouts_enabled", "kyc_level", "livemode", "created"}`` avec
    ``status`` ∈ ``pending_claim`` → ``linked`` (réclamé) → ``active`` (KYC validé) ; ``restricted`` et
    ``disabled`` coupent les encaissements. Les capacités sont posées par Sangho, jamais par la plateforme.
    """

    _path = "/connect/accounts/"

    def create(
        self,
        external_id: str,
        email: str,
        business_name: str = "",
        phone: str = "",
        *,
        idempotency_key: str | None = None,
    ) -> dict:
        """Crée (ou retrouve) le compte d'un vendeur — IDEMPOTENT par ``external_id`` ; la réponse a la même
        forme que le compte existe déjà ou non (anti-énumération).

        ``claim_token`` n'est renvoyé QU'À la création : transmettez-le au vendeur par e-mail, sans le
        stocker ni le journaliser (``reissue_claim_token`` en émet un nouveau).
        """
        self._client.assert_secret_key("connect.accounts.create")
        body = {"external_id": str(external_id), "email": email, "business_name": business_name, "phone": phone}
        return self._client.post(self._path, body=body, idempotency_key=idempotency_key)

    def retrieve(self, id: str) -> dict:
        """Lit un compte : statut, capacités et niveau KYC (resynchronisation, mode dégradé)."""
        self._client.assert_secret_key("connect.accounts.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def list(self) -> dict:
        """Liste les comptes de la plateforme (``{"object": "list", "data": [...]}``, non paginée)."""
        self._client.assert_secret_key("connect.accounts.list")
        return self._client.get(self._path)

    def reissue_claim_token(self, id: str) -> dict:
        """Réémet le jeton de réclamation d'un compte encore ``pending_claim`` ; l'ancien est invalidé."""
        self._client.assert_secret_key("connect.accounts.reissue_claim_token")
        return self._client.post(f"{self._path}{id}/claim-token/")

    def create_kyc_session(
        self,
        id: str,
        return_url: str,
        refresh_url: str = "",
        *,
        idempotency_key: str | None = None,
    ) -> dict:
        """Lance le KYC hébergé par Sangho ; redirigez le vendeur vers ``session["url"]`` (valable ~1 h).

        Le compte doit avoir été réclamé (sinon `SanghoConflictError`, code ``account_not_claimed``) ;
        les adresses doivent être en https. Le résultat revient par les événements ``kyc.updated`` /
        ``account.updated``.
        """
        self._client.assert_secret_key("connect.accounts.create_kyc_session")
        body = {"return_url": return_url}
        if refresh_url:
            body["refresh_url"] = refresh_url
        return self._client.post(f"{self._path}{id}/kyc-session/", body=body, idempotency_key=idempotency_key)

    def balance(self, id: str) -> dict:
        """Soldes du compte : ``available``, ``held``, ``frozen``, ``reserve``, ``negative``, ``paid_out`` (chaînes décimales) — source de vérité pour l'affichage."""
        self._client.assert_secret_key("connect.accounts.balance")
        return self._client.get(f"{self._path}{id}/balance/")

    def create_payout(self, id: str, amount, destination: str, *, idempotency_key: str) -> dict:
        """Retrait vers Mobile Money / banque : limité au disponible POSITIF (refus ``negative_balance`` / ``insufficient_available`` / KYC)."""
        self._client.assert_secret_key("connect.accounts.create_payout")
        key = _require_key("connect.accounts.create_payout", idempotency_key)
        return self._client.post(f"{self._path}{id}/payouts/", body={"amount": amount, "destination": destination}, idempotency_key=key)

    def list_payouts(self, id: str) -> dict:
        """Retraits du compte (``{"object": "list", "data": [...]}``)."""
        self._client.assert_secret_key("connect.accounts.list_payouts")
        return self._client.get(f"{self._path}{id}/payouts/")


class ConnectPayments(BaseResource):
    """``client.connect.payments`` — instructions sur un paiement avec répartition (``cpay_…``).

    Evangzat (la plateforme) DÉCIDE, Sangho EXÉCUTE : libérer, rembourser, geler. Création : ``checkout_sessions.create(…, connect={…})``.
    Montants renvoyés en chaînes décimales.
    """

    _path = "/connect/payments/"

    def retrieve(self, id: str) -> dict:
        """Lit le paiement : mode (``escrow`` / ``instant``), montants, commission, état."""
        self._client.assert_secret_key("connect.payments.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def release(self, id: str, *, idempotency_key: str) -> dict:
        """Libère les fonds bloqués (ou gelés) au vendeur, commission retenue. Idempotent ; ``funds.released``."""
        self._client.assert_secret_key("connect.payments.release")
        key = _require_key("connect.payments.release", idempotency_key)
        return self._client.post(f"{self._path}{id}/release/", body={}, idempotency_key=key)

    def refund(self, id: str, scope: str, amount=None, reason: str = "", *, idempotency_key: str) -> dict:
        """Rembourse le client. ``scope`` : ``product`` (livraison conservée), ``full`` (produit + livraison, reprise des frais déjà versés),
        ``amount`` (montant libre, ``amount`` requis)."""
        self._client.assert_secret_key("connect.payments.refund")
        key = _require_key("connect.payments.refund", idempotency_key)
        if scope not in ("product", "full", "amount"):
            raise SanghoValidationError(raw={"message": 'scope doit valoir "product", "full" ou "amount".'})
        body: dict = {"scope": scope}
        if amount is not None:
            body["amount"] = amount
        if reason:
            body["reason"] = reason
        return self._client.post(f"{self._path}{id}/refund/", body=body, idempotency_key=key)

    def freeze(self, id: str, *, idempotency_key: str | None = None) -> dict:
        """Bloqué → gelé (litige) ; ``funds.frozen``."""
        self._client.assert_secret_key("connect.payments.freeze")
        return self._client.post(f"{self._path}{id}/freeze/", body={}, idempotency_key=idempotency_key)

    def unfreeze(self, id: str, *, idempotency_key: str | None = None) -> dict:
        """Gelé → bloqué ; ``funds.unfrozen``."""
        self._client.assert_secret_key("connect.payments.unfreeze")
        return self._client.post(f"{self._path}{id}/unfreeze/", body={}, idempotency_key=idempotency_key)

    def simulate_payment(self, id: str) -> dict:
        """Sandbox uniquement : simule l'encaissement du paiement."""
        self._client.assert_secret_key("connect.payments.simulate_payment")
        return self._client.post(f"{self._path}{id}/simulate-payment/", body={})


class Connect(BaseResource):
    def __init__(self, client) -> None:
        super().__init__(client)
        self.accounts = ConnectAccounts(client)
        self.payments = ConnectPayments(client)
