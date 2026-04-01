from __future__ import annotations
from sangho._base import BaseResource


class Security(BaseResource):
    _path = "/security/"

    def retrieve(self) -> dict:
        """Retrieve the security profile for the current app."""
        self._client.assert_secret_key("security.retrieve")
        return self._client.get(self._path)

    def update(self, **payloads) -> dict:
        """Update security settings (IP whitelist, 2FA enforcement, etc.)."""
        self._client.assert_secret_key("security.update")
        return self._client.patch(self._path, body=payloads)

    def roll_secret_key(self) -> dict:
        """Rotate the secret key. Returns the new key (shown once)."""
        self._client.assert_secret_key("security.roll_secret_key")
        return self._client.post(f"{self._path}roll-secret/")

    def list_sessions(self, **criteria) -> dict:
        self._client.assert_secret_key("security.list_sessions")
        return self._client.get(f"{self._path}sessions/", params=criteria or None)

    def revoke_session(self, session_id: str) -> None:
        self._client.assert_secret_key("security.revoke_session")
        return self._client.delete(f"{self._path}sessions/{session_id}/")

    def options(self) -> dict:
        return self._client.options(self._path)
