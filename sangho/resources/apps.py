from __future__ import annotations

from sangho._base import BaseResource


class Apps(BaseResource):
    _path = "/apps/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("apps.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("apps.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, name: str, **opts) -> dict:
        self._client.assert_secret_key("apps.create")
        return self._client.post(self._path, body={"name": name, **opts})

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("apps.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def delete(self, id: str) -> None:
        self._client.assert_secret_key("apps.delete")
        return self._client.delete(f"{self._path}{id}/")

    def keys(self, id: str) -> dict:
        """Retrieve the current publishable/secret key pair for an app."""
        self._client.assert_secret_key("apps.keys")
        return self._client.get(f"{self._path}{id}/keys/")

    def roll_secret(self, id: str) -> dict:
        """Rotate the secret key for an app."""
        self._client.assert_secret_key("apps.roll_secret")
        return self._client.post(f"{self._path}{id}/roll-secret/")

    def options(self) -> dict:
        return self._client.options(self._path)
