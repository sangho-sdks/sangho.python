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
    amount=5000,
    customer="cust_xxx",
    currency="XAF",
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
            customer="cust_xxx",
            currency="XAF",
        )
        print(intent["id"])

asyncio.run(main())
```

## Gestion des erreurs

```python
import sangho

try:
    intent = client.payment_intents.create(amount=5000, customer="cust_xxx")
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

## Documentation

La documentation complète est disponible sur [docs.sangho.ga/api/sdks/python](https://docs.sangho.ga/api/sdks/python/).

## Ressources disponibles

`account` · `addresses` · `apps` · `customers` · `products` · `payment_intents` ·
`checkout_sessions` · `invoices` · `transactions` · `refunds` · `subscriptions` ·
`payment_methods` · `receipts` · `webhooks` · `payment_links` · `security` ·
`partners` · `terminal` · `sandbox`

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Changelog

Voir [CHANGELOG.md](CHANGELOG.md).

## Licence

MIT
