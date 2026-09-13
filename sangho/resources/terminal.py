from __future__ import annotations

from sangho._base import BaseResource


class _TerminalReaders(BaseResource):
    _path = "/terminal/readers/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("terminal.readers.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.readers.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, **payloads) -> dict:
        self._client.assert_secret_key("terminal.readers.create")
        return self._client.post(self._path, body=payloads)

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("terminal.readers.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def disable(self, id: str) -> dict:
        """Disable a reader (soft-delete)."""
        self._client.assert_secret_key("terminal.readers.disable")
        return self._client.delete(f"{self._path}{id}/")

    def refresh_token(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.readers.refresh_token")
        return self._client.post(f"{self._path}{id}/refresh-token/")

    def heartbeat(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.readers.heartbeat")
        return self._client.post(f"{self._path}{id}/heartbeat/")

    def options(self) -> dict:
        return self._client.options(self._path)


class _TerminalSessions(BaseResource):
    _path = "/terminal/sessions/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("terminal.sessions.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.sessions.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, **payloads) -> dict:
        self._client.assert_secret_key("terminal.sessions.create")
        return self._client.post(self._path, body=payloads)

    def present_payment_method(self, id: str, **payloads) -> dict:
        # Accepte aussi un reader_token (session terminal) — géré côté
        # backend (permission IsTerminalToken), pas seulement une clé secrète.
        self._client.assert_secret_key("terminal.sessions.present_payment_method")
        return self._client.post(f"{self._path}{id}/present-payment-method/", body=payloads)

    def poll_status(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.sessions.poll_status")
        return self._client.get(f"{self._path}{id}/status/")

    def cancel(self, id: str) -> dict:
        self._client.assert_secret_key("terminal.sessions.cancel")
        return self._client.post(f"{self._path}{id}/cancel/")

    def options(self) -> dict:
        return self._client.options(self._path)


class _TerminalOffline(BaseResource):
    _path = "/terminal/offline/sync/"

    def sync(self, **payloads) -> dict:
        self._client.assert_secret_key("terminal.offline.sync")
        return self._client.post(self._path, body=payloads)

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("terminal.offline.list")
        return self._client.get(self._path, params=criteria or None)

    def options(self) -> dict:
        return self._client.options(self._path)


class Terminal(BaseResource):
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
