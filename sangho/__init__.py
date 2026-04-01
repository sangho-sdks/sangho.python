"""
Sangho Python SDK
~~~~~~~~~~~~~~~~~
XAF-first payment SDK for Africa.

Basic usage::

    from sangho import Sangho

    client = Sangho("sk_test_xxx")
    customer = client.customers.create(email="jean@example.com", name="Jean Ondo")
"""
from sangho.sangho import Sangho
from sangho._errors import (
    SanghoError,
    SanghoAuthError,
    SanghoPublicKeyError,
    SanghoPermissionError,
    SanghoNotFoundError,
    SanghoIdempotencyError,
    SanghoValidationError,
    SanghoRateLimitError,
)

__version__ = "1.0.0"
__all__ = [
    "Sangho",
    "SanghoError",
    "SanghoAuthError",
    "SanghoPublicKeyError",
    "SanghoPermissionError",
    "SanghoNotFoundError",
    "SanghoIdempotencyError",
    "SanghoValidationError",
    "SanghoRateLimitError",
]
