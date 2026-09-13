from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Security(AsyncBaseResource):
    _path = "/security/"

    async def retrieve(self) -> dict:
        """Retrieve the security profile for the current app."""
        self._client.assert_secret_key("security.retrieve")
        return await self._client.get(f"{self._path}me/")

    async def update(self, **payloads) -> dict:
        """Update security settings (IP whitelist, 2FA enforcement, etc.)."""
        self._client.assert_secret_key("security.update")
        return await self._client.patch(f"{self._path}update_me/", body=payloads)

    async def add_allowed_ips(self, ips: list[str]) -> dict:
        """No dedicated backend action to add/remove IPs: re-read the
        profile, recompose the full list, then send it back via update()."""
        self._client.assert_secret_key("security.add_allowed_ips")
        profile = await self.retrieve()
        merged = list(dict.fromkeys([*profile.get("allowed_ips", []), *ips]))
        return await self.update(allowed_ips=merged)

    async def remove_allowed_ips(self, ips: list[str]) -> dict:
        self._client.assert_secret_key("security.remove_allowed_ips")
        profile = await self.retrieve()
        remaining = [ip for ip in profile.get("allowed_ips", []) if ip not in ips]
        return await self.update(allowed_ips=remaining)

    async def roll_secret_key(self) -> dict:
        """Rotate the secret key. Returns the new key (shown once)."""
        self._client.assert_secret_key("security.roll_secret_key")
        return await self._client.post(f"{self._path}roll-secret/")

    async def list_sessions(self, **criteria) -> dict:
        self._client.assert_secret_key("security.list_sessions")
        return await self._client.get(f"{self._path}sessions/", params=criteria or None)

    async def revoke_session(self, session_id: str) -> None:
        self._client.assert_secret_key("security.revoke_session")
        return await self._client.delete(f"{self._path}sessions/{session_id}/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
