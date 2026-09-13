from __future__ import annotations

from sangho._base import BaseResource


class Account(BaseResource):
    """
    sangho.account.retrieve()
    """

    _path = "/account/"

    def retrieve(self) -> dict:
        """
        Return the App associated with the secret key used for this request.

        Equivalent to ``apps.retrieve(id)`` without needing to know the id
        upfront — handy as a "who am I" / introspection health-check.
        """
        self._client.assert_secret_key("account.retrieve")
        return self._client.get(self._path)
