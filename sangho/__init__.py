"""
Sangho Python SDK
~~~~~~~~~~~~~~~~~
XAF-first payment SDK for Africa.

Basic usage::

    from sangho import Sangho

    client = Sangho("sk_test_xxx")
    customer = client.customers.create(email="jean@example.com", name="Jean Ondo")

Async usage::

    import asyncio
    from sangho import AsyncSangho

    async def main():
        async with AsyncSangho("sk_test_xxx") as client:
            customer = await client.customers.create(email="jean@example.com", name="Jean Ondo")

    asyncio.run(main())
"""

from sangho import error
from sangho._errors import (
    SanghoAuthError,
    SanghoConflictError,
    SanghoError,
    SanghoIdempotencyError,
    SanghoNetworkError,
    SanghoNotFoundError,
    SanghoPermissionError,
    SanghoPlatformPartnerRequiredError,
    SanghoPublicKeyError,
    SanghoRateLimitError,
    SanghoTimeoutError,
    SanghoValidationError,
    SanghoWebhookSignatureError,
)
from sangho.sangho import Sangho
from sangho.sangho_async import AsyncSangho

__version__ = "1.3.0"
__all__ = [
    "Sangho",
    "AsyncSangho",
    "error",
    "SanghoError",
    "SanghoAuthError",
    "SanghoPublicKeyError",
    "SanghoPermissionError",
    "SanghoPlatformPartnerRequiredError",
    "SanghoNotFoundError",
    "SanghoIdempotencyError",
    "SanghoConflictError",
    "SanghoWebhookSignatureError",
    "SanghoValidationError",
    "SanghoRateLimitError",
    "SanghoNetworkError",
    "SanghoTimeoutError",
]
