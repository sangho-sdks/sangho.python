"""
Sangho SDK — Error hierarchy
All errors extend SanghoError (itself a subclass of Exception).
"""
from __future__ import annotations

import httpx


class SanghoError(Exception):
    """Base error for all Sangho API errors."""

    def __init__(
        self,
        message: str,
        code: str = "api_error",
        status_code: int | None = None,
        raw: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.raw = raw or {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"status_code={self.status_code!r})"
        )


class SanghoAuthError(SanghoError):
    """401 — Invalid or missing API key."""


class SanghoPublicKeyError(SanghoError):
    """403 — Operation requires a secret key, but a public key was used."""

    def __init__(self, method: str):
        super().__init__(
            f"Method `{method}` requires a secret key (sk_…). "
            "You provided a public key (pk_…).",
            code="public_key_not_allowed",
            status_code=403,
        )


class SanghoPermissionError(SanghoError):
    """403 — Forbidden (other than public key restriction)."""


class SanghoNotFoundError(SanghoError):
    """404 — Resource not found."""


class SanghoIdempotencyError(SanghoError):
    """409 — Idempotency key conflict."""


class SanghoValidationError(SanghoError):
    """422 — Request validation failed."""

    @property
    def field_errors(self) -> dict[str, list[str]]:
        detail = self.raw.get("detail") or self.raw.get("errors") or {}
        return detail if isinstance(detail, dict) else {}


class SanghoRateLimitError(SanghoError):
    """429 — Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded.", retry_after: int = 60, raw: dict | None = None):
        super().__init__(message, code="rate_limit_exceeded", status_code=429, raw=raw)
        self.retry_after = retry_after


def _raise_for_status(response: httpx.Response, data: dict) -> None:
    """Raise the appropriate SanghoError based on HTTP status code."""
    message: str = data.get("message") or data.get("detail") or "API error"
    if isinstance(message, dict | list):
        message = str(message)
    code: str | None = data.get("code")

    match response.status_code:
        case 401:
            raise SanghoAuthError(message, status_code=401, raw=data)
        case 403:
            if code == "public_key_not_allowed":
                raise SanghoPublicKeyError("Operation")
            raise SanghoPermissionError(message, code=code or "permission_denied", status_code=403, raw=data)
        case 404:
            raise SanghoNotFoundError(message, status_code=404, raw=data)
        case 409:
            raise SanghoIdempotencyError(message, code="idempotency_conflict", status_code=409, raw=data)
        case 422:
            raise SanghoValidationError(message, code="validation_error", status_code=422, raw=data)
        case 429:
            retry = int(data.get("retry_later") or response.headers.get("Retry-After", 60))
            raise SanghoRateLimitError(message, retry_after=retry, raw=data)
        case _:
            raise SanghoError(message, status_code=response.status_code, raw=data)
