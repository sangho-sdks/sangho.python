from __future__ import annotations

from sangho._base_async import AsyncBaseResource


class Account(AsyncBaseResource):
    """
    sangho.account.retrieve()
    """

    _path = "/account/"

    async def retrieve(self) -> dict:
        """
        Return the App associated with the secret key used for this request.

        Equivalent to ``apps.retrieve(id)`` without needing to know the id
        upfront — handy as a "who am I" / introspection health-check.
        """
        self._client.assert_secret_key("account.retrieve")
        return await self._client.get(self._path)
