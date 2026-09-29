"""
Sangho SDK — Error hierarchy
All errors extend SanghoError (itself a subclass of Exception).

Mirrors the JS SDK's error hierarchy (@/core/errors.ts): a shared `type`
(broad category) and `code` (precise backend code) on every error, plus two
SDK-only categories — SanghoNetworkError / SanghoTimeoutError — for requests
that never reached the backend.
"""

from __future__ import annotations

import httpx

KNOWN_ERROR_TYPES = frozenset(
    {
        "AUTHENTICATION_ERROR",
        "PERMISSION_ERROR",
        "NOT_FOUND_ERROR",
        "CONFLICT_ERROR",
        "VALIDATION_ERROR",
        "RATE_LIMIT_ERROR",
        "API_ERROR",
        "NETWORK_ERROR",
        "TIMEOUT_ERROR",
    }
)


def _resolve_type(default_type: str, raw: dict | None) -> str:
    """If the backend sent a recognized `type`, it wins (1:1 mapping);
    otherwise fall back to the category implied by the subclass used."""
    backend_type = (raw or {}).get("type")
    if isinstance(backend_type, str) and backend_type.upper() in KNOWN_ERROR_TYPES:
        return backend_type.upper()
    return default_type


class SanghoError(Exception):
    """Base error for all Sangho API errors."""

    def __init__(
        self,
        message: str,
        code: str = "api_error",
        status_code: int | None = None,
        raw: dict | None = None,
        type_: str = "API_ERROR",
    ):
        super().__init__(message)
        self.message = message
        self.raw = raw or {}
        self.type = _resolve_type(type_, self.raw)
        # Le code métier précis renvoyé par le backend (raw.code) prime toujours
        # sur le code par défaut de la sous-classe, à l'image du SDK JS.
        self.code = self.raw.get("code") or code
        self.status_code = status_code

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"type={self.type!r}, "
            f"code={self.code!r}, "
            f"status_code={self.status_code!r})"
        )


class SanghoAuthError(SanghoError):
    """401 — Invalid or missing API key."""

    def __init__(
        self,
        message: str = "Invalid or missing API key.",
        status_code: int = 401,
        raw: dict | None = None,
    ):
        super().__init__(
            message,
            code="authentication_error",
            status_code=status_code,
            raw=raw,
            type_="AUTHENTICATION_ERROR",
        )


class SanghoPublicKeyError(SanghoError):
    """403 — Operation requires a secret key, but a public key was used."""

    def __init__(
        self,
        message: str = "Public key not allowed for this operation.",
        raw: dict | None = None,
    ):
        super().__init__(
            message,
            code="public_key_not_allowed",
            status_code=403,
            raw=raw,
            type_="PERMISSION_ERROR",
        )

    @classmethod
    def for_method(cls, method: str) -> SanghoPublicKeyError:
        """Raised client-side (before any request) by ``HttpClient.assert_secret_key``."""
        return cls(
            f"Method `{method}` requires a secret key (sk_…). You provided a public key (pk_…)."
        )


class SanghoPermissionError(SanghoError):
    """403 — Forbidden (other than public key restriction)."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        status_code: int = 403,
        raw: dict | None = None,
        code: str = "permission_denied",
    ):
        super().__init__(
            message,
            code=code,
            status_code=status_code,
            raw=raw,
            type_="PERMISSION_ERROR",
        )


class SanghoPlatformPartnerRequiredError(SanghoPermissionError):
    """403 — App valide (clé secrète correcte) mais sans le statut **Partenaire
    Plateforme** requis pour appeler ``connect.*``. Ce statut est accordé
    manuellement par Sangho (revue back-office) après une demande faite depuis
    le dashboard — ce n'est pas une histoire de clé ou de plan tarifaire, donc
    distinct de `SanghoPublicKeyError`. Sous-classe de `SanghoPermissionError` :
    un `except SanghoPermissionError` générique continue de l'attraper.
    """

    def __init__(
        self,
        message: str = (
            "This App does not have Platform Partner status. Request it from the "
            "Sangho dashboard before calling Connect endpoints."
        ),
        raw: dict | None = None,
    ):
        super().__init__(message, raw=raw, code="platform_partner_required")


class SanghoNotFoundError(SanghoError):
    """404 — Resource not found."""

    def __init__(
        self, message: str = "Resource not found.", status_code: int = 404, raw: dict | None = None
    ):
        super().__init__(
            message, code="not_found", status_code=status_code, raw=raw, type_="NOT_FOUND_ERROR"
        )


class SanghoIdempotencyError(SanghoError):
    """409 — Idempotency key reused with a different request payload."""

    def __init__(self, raw: dict | None = None):
        super().__init__(
            "Idempotency key reused with different request parameters.",
            code="idempotency_conflict",
            status_code=409,
            raw=raw,
            type_="CONFLICT_ERROR",
        )


class SanghoValidationError(SanghoError):
    """422 — Request validation failed (field-by-field errors)."""

    def __init__(self, raw: dict | None = None):
        raw = raw or {}
        detail = raw.get("detail")
        fields: dict[str, list[str]] = (
            detail if isinstance(detail, dict) else (raw.get("errors") or {})
        )
        summary = " | ".join(f"{k}: {', '.join(v)}" for k, v in fields.items()) if fields else ""
        message = summary or raw.get("message") or "Validation error"
        super().__init__(
            message, code="validation_error", status_code=422, raw=raw, type_="VALIDATION_ERROR"
        )
        self.field_errors: dict[str, list[str]] = fields

    @property
    def param(self) -> str | None:
        return self.raw.get("param")


class SanghoRateLimitError(SanghoError):
    """429 — Too many requests. `retry_after` is the delay (seconds) before retry."""

    def __init__(self, retry_after: int | None = None, raw: dict | None = None):
        raw = raw or {}
        message = raw.get("message") or (
            f"Rate limit exceeded. Retry after {retry_after}s."
            if retry_after
            else "Rate limit exceeded."
        )
        super().__init__(
            message, code="rate_limit_exceeded", status_code=429, raw=raw, type_="RATE_LIMIT_ERROR"
        )
        self.retry_after = retry_after


class SanghoConflictError(SanghoError):
    """409 — Conflit d'état métier autre qu'une clé d'idempotence (ex : `account_not_claimed`, `account_disabled`).
    Le code précis est dans `code`."""

    def __init__(
        self,
        message: str = "Conflict with the current state of the resource.",
        raw: dict | None = None,
    ):
        super().__init__(
            message, code="conflict", status_code=409, raw=raw, type_="CONFLICT_ERROR"
        )


class SanghoWebhookSignatureError(SanghoError):
    """Signature de webhook refusée. `reason` : ``malformed`` (en-tête illisible, statut 400),
    ``expired`` (horodatage hors tolérance, 400) ou ``mismatch`` (aucune signature ne correspond, 401).

    Sous-classe de `SanghoError` : les anciens ``except SanghoError`` continuent de fonctionner, et
    `code` garde les valeurs historiques (``invalid_signature``, ``stale_event``)."""

    def __init__(self, reason: str, message: str):
        super().__init__(
            message,
            code="invalid_signature" if reason != "expired" else "stale_event",
            status_code=401 if reason == "mismatch" else 400,
            type_="AUTHENTICATION_ERROR" if reason == "mismatch" else "VALIDATION_ERROR",
        )
        self.reason = reason


class SanghoNetworkError(SanghoError):
    """Network error (no response from the server). SDK-only category — the
    request never reached the backend, so there is no `raw`/business `code`."""

    def __init__(self, message: str = "Network error. Please check your connection."):
        super().__init__(message, code="network_error", type_="NETWORK_ERROR")


class SanghoTimeoutError(SanghoError):
    """Request timed out. SDK-only category, same reasoning as `SanghoNetworkError`."""

    def __init__(self, timeout: float):
        super().__init__(
            f"Request timed out after {timeout}s.", code="timeout_error", type_="TIMEOUT_ERROR"
        )


def _raise_for_status(response: httpx.Response, data: dict) -> None:
    """Raise the appropriate SanghoError based on the HTTP status code."""
    # Les routes Connect renvoient `{"error": {"code", "message"}}` : on aplatit pour lire le même format partout.
    nested = data.get("error") if isinstance(data, dict) else None
    if isinstance(nested, dict):
        data = {**data, **nested}
    message = data.get("message") or data.get("detail") or "API error"
    if isinstance(message, (dict, list)):
        message = str(message)

    # Insensible à la casse : le backend envoie tantôt "PUBLIC_KEY_NOT_ALLOWED"
    # (catalogue d'erreurs DRF moderne), tantôt "public_key_not_allowed"
    # (ancien décorateur Django) selon le chemin qui a rejeté la requête.
    raw_code = data.get("code")
    code = raw_code.lower() if isinstance(raw_code, str) else None

    match response.status_code:
        case 401:
            raise SanghoAuthError(message, raw=data)
        case 403:
            if code == "public_key_not_allowed":
                raise SanghoPublicKeyError(message, raw=data)
            if code == "platform_partner_required":
                raise SanghoPlatformPartnerRequiredError(message, raw=data)
            raise SanghoPermissionError(message, raw=data)
        case 404:
            raise SanghoNotFoundError(message, raw=data)
        case 409:
            # Sans code (ancien backend) ou `idempotency_conflict` : clé d'idempotence rejouée avec un autre
            # corps ; tout autre code est un conflit d'état métier (ex : `account_not_claimed`).
            if not code or code == "idempotency_conflict":
                raise SanghoIdempotencyError(raw=data)
            raise SanghoConflictError(message, raw=data)
        case 422:
            raise SanghoValidationError(raw=data)
        case 429:
            retry_after = data.get("retry_after")
            if retry_after is None:
                retry_after = response.headers.get("Retry-After", 60)
            raise SanghoRateLimitError(retry_after=int(retry_after), raw=data)
        case _:
            raise SanghoError(message, status_code=response.status_code, raw=data)
