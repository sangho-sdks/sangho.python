from __future__ import annotations

from sangho._base import BaseResource


class Security(BaseResource):
    _path = "/security/"

    def retrieve(self) -> dict:
        """Retrieve the security profile for the current app."""
        self._client.assert_secret_key("security.retrieve")
        return self._client.get(f"{self._path}me/")

    def update(self, **payloads) -> dict:
        """Update security settings (IP whitelist, 2FA enforcement, etc.)."""
        self._client.assert_secret_key("security.update")
        return self._client.patch(f"{self._path}update_me/", body=payloads)

    def add_allowed_ips(self, ips: list[str]) -> dict:
        """No dedicated backend action to add/remove IPs: re-read the
        profile, recompose the full list, then send it back via update()."""
        self._client.assert_secret_key("security.add_allowed_ips")
        profile = self.retrieve()
        merged = list(dict.fromkeys([*profile.get("allowed_ips", []), *ips]))
        return self.update(allowed_ips=merged)

    def remove_allowed_ips(self, ips: list[str]) -> dict:
        self._client.assert_secret_key("security.remove_allowed_ips")
        profile = self.retrieve()
        remaining = [ip for ip in profile.get("allowed_ips", []) if ip not in ips]
        return self.update(allowed_ips=remaining)

    def options(self) -> dict:
        return self._client.options(self._path)
