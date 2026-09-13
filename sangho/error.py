"""
Alias module exposing Sangho's error classes under familiar names
(``sangho.error.AuthenticationError``, etc.), à la Stripe.

These are aliases, not a parallel hierarchy: ``sangho.error.AuthenticationError``
*is* ``sangho.SanghoAuthError`` (same class, two import paths), so
``except sangho.error.AuthenticationError`` and ``except sangho.SanghoAuthError``
catch exactly the same exception.
"""

from __future__ import annotations

from sangho._errors import SanghoAuthError as AuthenticationError
from sangho._errors import SanghoError as SanghoError
from sangho._errors import SanghoIdempotencyError as IdempotencyError
from sangho._errors import SanghoNetworkError as APIConnectionError
from sangho._errors import SanghoNotFoundError as NotFoundError
from sangho._errors import SanghoPermissionError as PermissionError
from sangho._errors import SanghoPublicKeyError as PublicKeyError
from sangho._errors import SanghoRateLimitError as RateLimitError
from sangho._errors import SanghoTimeoutError as APITimeoutError
from sangho._errors import SanghoValidationError as InvalidRequestError

__all__ = [
    "SanghoError",
    "AuthenticationError",
    "PermissionError",
    "PublicKeyError",
    "NotFoundError",
    "IdempotencyError",
    "InvalidRequestError",
    "RateLimitError",
    "APIConnectionError",
    "APITimeoutError",
]
