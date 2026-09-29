# Sangho Python SDK

SDK officiel Python pour l'API [Sangho](https://sangho.ga) — paiements XAF pour l'Afrique.

[![PyPI version](https://badge.fury.io/py/sangho.svg)](https://badge.fury.io/py/sangho)
[![CI](https://github.com/sangho-sdks/sangho.py/actions/workflows/ci.yml/badge.svg)](https://github.com/sangho-sdks/sangho.py/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Installation

```bash
pip install sangho
```

## Quickstart

```python
import sangho

client = sangho.Sangho("sk_prod_...")

# Créer un payment intent
intent = client.payment_intents.create(
    amount=5000,               # unité majeure : 5000 XAF (jamais en centimes)
    currency="XAF",
    customer_email="ada@example.com",
)

print(intent["id"])
```

## Async

Chaque appel devient une coroutine — utile sous FastAPI/aiohttp/asyncio :

```python
import asyncio
from sangho import AsyncSangho

async def main():
    async with AsyncSangho("sk_prod_...") as client:
        intent = await client.payment_intents.create(
            amount=5000,
            currency="XAF",
            customer_email="ada@example.com",
        )
        print(intent["id"])

asyncio.run(main())
```

## Gestion des erreurs

```python
import sangho

try:
    intent = client.payment_intents.create(amount=5000, currency="XAF")
except sangho.error.AuthenticationError:
    print("Clé API invalide")
except sangho.error.RateLimitError as e:
    print("Trop de requêtes, retenter après", e.retry_after, "s")
except sangho.error.InvalidRequestError as e:
    print(e.param, e.message)
except sangho.error.SanghoError as e:
    print(e.code, e.message, e.status_code)
```

`sangho.error.*` sont des alias des classes `sangho.SanghoXxxError` (mêmes
exceptions, deux chemins d'import) : `except sangho.error.AuthenticationError`
et `except sangho.SanghoAuthError` interceptent exactement la même erreur.

## Marketplace / Connect

Une plateforme (ex. une place de marché) crée un compte Sangho par vendeur ; Sangho reste seul responsable du
paiement et du **KYC** (la plateforme ne collecte ni ne stocke aucune pièce d'identité). Clé secrète requise
**et** l'App appelante doit avoir le statut **Partenaire Plateforme** — accordé manuellement par Sangho (revue
back-office) après une demande faite depuis le dashboard, pas une simple histoire de clé ou de plan tarifaire.
Une App marchande ordinaire (B2C, sans ce statut) reçoit un 403 `SanghoPlatformPartnerRequiredError` :

```python
import sangho

try:
    client.connect.accounts.list()
except sangho.SanghoPlatformPartnerRequiredError:
    ...  # Cette App n'a pas (encore) le statut Partenaire Plateforme.
```

```python
import sangho

client = sangho.Sangho("sk_prod_...")

# 1. Créer le compte du vendeur — idempotent par external_id (même réponse qu'il existe déjà ou non)
account = client.connect.accounts.create(
    external_id="seller-42",
    email="ada@example.com",
    business_name="Boutique Ada",
    idempotency_key="connect-account-seller-42",
)
# account["status"] == "pending_claim". `claim_token` n'est renvoyé QU'À la création : envoyez-le au
# vendeur par e-mail (lien de réclamation Sangho), sans le stocker ni le journaliser.
# Perdu ou expiré : client.connect.accounts.reissue_claim_token(account["id"]) (l'ancien est invalidé)

# 2. Une fois le compte réclamé par le vendeur, lancer le KYC hébergé par Sangho
try:
    session = client.connect.accounts.create_kyc_session(
        account["id"],
        return_url="https://maplateforme.com/wallet/",   # https obligatoire
        refresh_url="https://maplateforme.com/wallet/",
    )
    # Redirigez le vendeur vers session["url"] (valable environ une heure)
except sangho.SanghoConflictError as e:
    if e.code == "account_not_claimed":
        ...  # le vendeur n'a pas encore réclamé son compte

# 3. Le résultat arrive par webhook : `kyc.updated` et `account.updated` (payload = compte à jour)
event = sangho.Sangho.construct_event(raw_body, request.headers["Sangho-Signature"], webhook_secret)
if event["type"] == "kyc.updated":
    account = event["data"]["object"]
    if account["charges_enabled"]:
        ...  # n'exposez les produits du vendeur que si les encaissements sont activés

# Relecture (resynchronisation périodique, mode dégradé)
current = client.connect.accounts.retrieve(account["id"])
```

Statuts : `pending_claim` → `linked` (réclamé) → `active` (KYC validé) ; `restricted` (capacités limitées) et
`disabled` (désactivé par Sangho) coupent les encaissements. La version asynchrone est identique
(`await client.connect.accounts.create(...)`).

### Paiement sécurisé à la livraison (séquestre)

```python
session = client.checkout_sessions.create(
    [{"name": "Robe", "unit_amount": 25000, "quantity": 1}],
    success_url="https://boutique.example/checkout/return/42",
    shipping_amount=2000,
    connect={"account": account["id"], "mode": "escrow", "commission": 1250, "external_reference": "ORDER-42"},
)
payment_id = session["connect_payment"]                     # cpay_…

# Livraison confirmée par la plateforme : libérer les fonds (clé d'idempotence OBLIGATOIRE)
client.connect.payments.release(payment_id, idempotency_key="release-ORDER-42")

# Litige : geler, puis libérer ou rembourser
client.connect.payments.freeze(payment_id)
client.connect.payments.refund(payment_id, "product", reason="non livré", idempotency_key="refund-ORDER-42")

balance = client.connect.accounts.balance(account["id"])   # available, held, frozen, reserve, negative, paid_out
client.connect.accounts.create_payout(account["id"], "5000", "mobile:077000000", idempotency_key="payout-42-1")
```

Événements à traiter (idempotemment) : `payment.succeeded`, `funds.released`, `funds.frozen`, `refund.succeeded`, `clawback.succeeded`, `payout.paid`, `account.verified`…

## Webhooks

`Sangho.construct_event(corps_brut, en_tête, secret)` vérifie `Sangho-Signature: t=<ts>,v1=<hex>` (HMAC-SHA256 de
`"<ts>.<corps brut>"`, tolérance 5 min par défaut, comparaison à temps constant). Passez le corps **brut** (octets),
jamais un JSON re-sérialisé. Pendant une rotation de secret, passez une liste (`[nouveau, ancien]`) ; plusieurs `v1`
dans l'en-tête sont acceptés. En cas de refus : `sangho.SanghoWebhookSignatureError` (sous-classe de `SanghoError`) avec
`reason` ∈ `malformed` / `expired` / `mismatch`. Pour tester votre endpoint : `Sangho.generate_test_header(corps, secret)`.

## Idempotence

Toute méthode d'écriture accepte `idempotency_key="..."` : rejouer un appel avec la **même** clé et le même corps renvoie la
même réponse ; la même clé avec un corps différent lève `SanghoIdempotencyError` (409). Sans clé, le SDK en génère une
nouvelle à chaque appel et **ne rejoue pas** un POST après un timeout ou une erreur réseau (le serveur a pu le traiter) ;
avec une clé fournie, ce rejeu est sûr et activé.

## Documentation

La documentation complète est disponible sur [docs.sangho.ga/api/sdks/python](https://docs.sangho.ga/api/sdks/python/).

## Ressources disponibles

`account` · `addresses` · `apps` · `customers` · `products` · `payment_intents` ·
`checkout_sessions` · `invoices` · `transactions` · `refunds` · `subscriptions` ·
`payment_methods` · `receipts` · `webhooks` · `payment_links` · `security` ·
`partners` · `terminal` · `sandbox` · `connect`

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Changelog

Voir [CHANGELOG.md](CHANGELOG.md).

## Licence

MIT
