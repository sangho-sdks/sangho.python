# Sangho Python SDK

SDK officiel Python pour l'API [Sangho](https://sangho.africa) — paiements XAF pour l'Afrique.

[![PyPI version](https://badge.fury.io/py/sangho.svg)](https://badge.fury.io/py/sangho)
[![CI](https://github.com/sangho-sdks/sangho-python/actions/workflows/ci.yml/badge.svg)](https://github.com/sangho-sdks/sangho-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Installation

```bash
pip install sangho
```

## Quickstart

```python
import sangho

client = sangho.Sangho(secret_key="sk_live_...")

# Créer un payment intent
intent = client.payment_intents.create({
    "amount": 5000,
    "currency": "XAF",
    "customer": "cust_xxx"
})

print(intent["id"])
```

## Documentation

La documentation complète est disponible sur [docs.sangho.africa](https://docs.sangho.africa).

## Ressources disponibles

`apps` · `customers` · `products` · `payment_intents` · `checkout_sessions` ·
`invoices` · `transactions` · `refunds` · `subscriptions` · `payment_methods` ·
`webhooks` · `payment_links` · `addresses` · `partners`

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Changelog

Voir [CHANGELOG.md](CHANGELOG.md).

## Licence

MIT
