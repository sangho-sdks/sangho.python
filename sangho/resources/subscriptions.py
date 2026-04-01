from __future__ import annotations
from sangho._base import BaseResource


class Subscriptions(BaseResource):
    _path = "/subscriptions/"

    def list(self, **criteria) -> dict:
        self._client.assert_secret_key("subscriptions.list")
        return self._client.get(self._path, params=criteria or None)

    def retrieve(self, id: str) -> dict:
        self._client.assert_secret_key("subscriptions.retrieve")
        return self._client.get(f"{self._path}{id}/")

    def create(self, customer: str, plan: str, **opts) -> dict:
        self._client.assert_secret_key("subscriptions.create")
        return self._client.post(self._path, body={"customer": customer, "plan": plan, **opts})

    def update(self, id: str, **payloads) -> dict:
        self._client.assert_secret_key("subscriptions.update")
        return self._client.patch(f"{self._path}{id}/", body=payloads)

    def cancel(self, id: str, **opts) -> dict:
        """Cancel at period end or immediately."""
        self._client.assert_secret_key("subscriptions.cancel")
        return self._client.post(f"{self._path}{id}/cancel/", body=opts)

    def pause(self, id: str) -> dict:
        self._client.assert_secret_key("subscriptions.pause")
        return self._client.post(f"{self._path}{id}/pause/")

    def resume(self, id: str) -> dict:
        self._client.assert_secret_key("subscriptions.resume")
        return self._client.post(f"{self._path}{id}/resume/")

    def options(self) -> dict:
        return self._client.options(self._path)
