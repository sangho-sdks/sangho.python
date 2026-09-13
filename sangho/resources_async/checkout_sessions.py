from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class CheckoutSessions(AsyncBaseResource):
    _path = "/checkout-sessions/"

    async def list(self, **criteria) -> dict:
        self._client.assert_secret_key("checkout_sessions.list")
        return await self._client.get(self._path, params=criteria or None)

    async def retrieve(self, id: str) -> dict:
        # Le backend autorise explicitement la clé publique sur cette action
        # (page de confirmation côté navigateur) — ne pas la bloquer ici.
        return await self._client.get(f"{self._path}{id}/")

    async def create(self, amount: int, success_url: str, cancel_url: str, **opts) -> dict:
        """
        Args:
            amount: Amount in XAF.
            success_url: Redirect URL on success.
            cancel_url: Redirect URL on cancel.
        """
        self._client.assert_secret_key("checkout_sessions.create")
        return await self._client.post(
            self._path,
            body={"amount": amount, "success_url": success_url, "cancel_url": cancel_url, **opts},
        )

    async def expire(self, id: str) -> dict:
        self._client.assert_secret_key("checkout_sessions.expire")
        return await self._client.post(f"{self._path}{id}/expire/")

    async def delete(self, id: str) -> dict:
        self._client.assert_secret_key("checkout_sessions.delete")
        return await self._client.delete(f"{self._path}{id}/")

    async def options(self) -> dict:
        return await self._client.options(self._path)
