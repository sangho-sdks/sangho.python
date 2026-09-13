from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class _TerminalReaders(AsyncBaseResource):
    _path = "/terminal/readers/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("terminal.readers.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.readers.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, **payloads) -> dict:
        self._client.assert_secret_key("terminal.readers.create")
        return await self._client.post(self._path, body=payloads)

    async def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("terminal.readers.update")
        return await self._client.patch(f"{self._path}{id}/", body=payloads)

    async def disable(self, id: str) -> dict:
        """Disable a reader (soft-delete)."""
        self._client.assert_secret_key("terminal.readers.disable")
        return await self._client.delete(f"{self._path}{id}/")

    async def refresh_token(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.readers.refresh_token")
        return await self._client.post(f"{self._path}{id}/refresh-token/")

    async def heartbeat(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.readers.heartbeat")
        return await self._client.post(f"{self._path}{id}/heartbeat/")

    async def options(self) -> dict:
        return await self._client.options(self._path)


class _TerminalSessions(AsyncBaseResource):
    _path = "/terminal/sessions/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("terminal.sessions.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.sessions.retrieve")
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, **payloads) -> dict:
        self._client.assert_secret_key("terminal.sessions.create")
        return await self._client.post(self._path, body=payloads)

    async def present_payment_method(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("terminal.sessions.present_payment_method")
        return await self._client.post(f"{self._path}{id}/present-payment-method/", body=payloads)

    async def poll_status(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.sessions.poll_status")
        return await self._client.get(f"{self._path}{id}/status/")

    async def cancel(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.sessions.cancel")
        return await self._client.post(f"{self._path}{id}/cancel/")

    async def options(self) -> dict:
        return await self._client.options(self._path)


class _TerminalOffline(AsyncBaseResource):
    _path = "/terminal/offline/sync/"

    async def sync(self, **payloads) -> dict:
        self._client.assert_secret_key("terminal.offline.sync")
        return await self._client.post(self._path, body=payloads)

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("terminal.offline.list")
        return await self._client.get(self._path, params=criteria or None)

    async def options(self) -> dict:
        return await self._client.options(self._path)


class Terminal(AsyncBaseResource):
    """
    sangho.terminal.readers.*   — gestion des lecteurs de carte physiques
    sangho.terminal.sessions.*  — sessions de paiement in-person
    sangho.terminal.offline.*   — synchronisation des transactions hors-ligne
    """

    def __init__(self, client) -> None:
        super().__init__(client)
        self.readers = _TerminalReaders(client)
        self.sessions = _TerminalSessions(client)
        self.offline = _TerminalOffline(client)
