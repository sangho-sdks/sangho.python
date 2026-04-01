# Sangho Python SDK

Official Python SDK for the [Sangho](https://sangho.com) payment platform — XAF-first, built for francophone Africa.

## Installation

```bash
pip install sangho
```

## Quick Start

```python
from sangho import Sangho

client = Sangho("sk_test_xxx")

# Create a customer
customer = client.customers.create(email="jean@example.com", name="Jean Ondo")

# Create a payment intent
intent = client.payment_intents.create(amount=25000, customer=customer["id"])

# Confirm payment
confirmed = client.payment_intents.confirm(intent["id"])
```

## Error Handling

```python
from sangho import SanghoValidationError, SanghoNotFoundError, SanghoRateLimitError

try:
    client.invoices.pay("inv_xxx")
except SanghoValidationError as e:
    print(e.field_errors)
except SanghoNotFoundError:
    print("Invoice not found")
except SanghoRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
```

## Webhook Verification

```python
from sangho.resources.webhooks import Webhooks

event = Webhooks.construct_event(
    payload=request.body,
    signature_header=request.headers["Sangho-Signature"],
    secret="whsec_xxx",
)
```

## Requirements

- Python 3.10+
- httpx >= 0.27
