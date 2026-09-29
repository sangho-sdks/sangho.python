from __future__ import annotations

import builtins

from sangho._base_async import AsyncBaseResource
from sangho.resources.webhooks import Webhooks as _SyncWebhooks


class Webhooks(AsyncBaseResource):
    _path = "/webhooks/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("webhooks.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("webhooks.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    # `builtins.list` plutôt que `list` : cette classe déclare sa propre
    # méthode `list` ci-dessus, qui masque le type builtin `list` dans
    # l'espace de noms de la classe pour la résolution des annotations
    # différées (from __future__ import annotations) — sans ce préfixe,
    # mypy résout `list[str]` vers `Webhooks.list` et non vers le builtin.
    async def create(self, url: str, events: builtins.list[str], **opts) -> dict:
        self._client.assert_secret_key("webhooks.create")
        return await self._client.post(self._path, body={"url": url, "events": events, **opts})

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("webhooks.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def delete(self, id: str) -> None:
        self._client.assert_secret_key("webhooks.delete")
        return await self._client.delete(f"{self._path}{id}/")

    async def roll_secret(self, id: str) -> dict:
        self._client.assert_secret_key("webhooks.roll_secret")
        return await self._client.post(f"{self._path}{id}/roll-secret/")

    async def send_test_event(self, id: str, event_type: str) -> dict:
        self._client.assert_secret_key("webhooks.send_test_event")
        return await self._client.post(f"{self._path}{id}/test/", body={"event_type": event_type})

    async def list_deliveries(self, id: str, **criteria) -> dict:
        self._client.assert_secret_key("webhooks.list_deliveries")
        return await self._client.get(f"{self._path}{id}/deliveries/", params=criteria or None)

    async def retry_delivery(self, id: str, delivery_id: str) -> dict:
        self._client.assert_secret_key("webhooks.retry_delivery")
        return await self._client.post(f"{self._path}{id}/deliveries/{delivery_id}/retry/")

    async def options(self) -> dict:
        return await self._client.options(self._path)

    # Vérification de signature = calcul HMAC pur, sans I/O réseau : on
    # réutilise directement l'implémentation synchrone plutôt que de la
    # dupliquer (une seule source de vérité pour la logique crypto).
    construct_event = staticmethod(_SyncWebhooks.construct_event)
    generate_test_header = staticmethod(_SyncWebhooks.generate_test_header)
