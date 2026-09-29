"""Common TypedDicts shared across resources."""

from __future__ import annotations

from typing import TypedDict


class PaginatedResponse(TypedDict):
    count: int
    next: str | None
    previous: str | None
    data: list[dict]


class CustomerDict(TypedDict, total=False):
    id: str
    object: str
    app: str
    email: str
    name: str
    phone: str | None
    status: str
    is_blacklisted: bool
    transactions_count: int
    total_spent: int
    metadata: dict
    created_at: str
    updated_at: str


class ProductDict(TypedDict, total=False):
    id: str
    object: str
    name: str
    price: int
    description: str | None
    status: str
    metadata: dict
    created_at: str
    updated_at: str
