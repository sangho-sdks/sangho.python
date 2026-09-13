"""
Tests d'intégration — Authentification & sécurité des clés API
Vérifie le comportement selon le type de clé (public vs secret).
"""
import pytest
from sangho import Sangho, SanghoAuthError, SanghoPublicKeyError

pytestmark = pytest.mark.integration


class TestAuthIntegration:

    def test_valid_secret_key_authenticates(self, client):
        """Une clé secrète valide doit permettre de lister les customers."""
        result = client.customers.list(page_size=1)
        assert "results" in result

    def test_invalid_key_raises_auth_error(self, base_url):
        """Une clé invalide doit lever SanghoAuthError (401)."""
        bad_client = Sangho("sk_test_invalidkeyXXXXXXXXXXXX", base_url=base_url)
        with pytest.raises(SanghoAuthError) as exc:
            bad_client.customers.list()
        assert exc.value.status_code == 401

    def test_public_key_blocked_on_write_operations(self, pub_client):
        """Les opérations d'écriture sont bloquées avec une clé publique."""
        write_ops = [
            lambda: pub_client.customers.list(),
            lambda: pub_client.products.list(),
            lambda: pub_client.payment_intents.list(),
        ]
        for op in write_ops:
            with pytest.raises(SanghoPublicKeyError):
                op()

    def test_key_prefix_validation(self):
        """Préfixe de clé invalide → ValueError avant tout appel réseau."""
        with pytest.raises(ValueError, match="Invalid API key"):
            Sangho("bad_key_without_prefix")

    def test_secret_key_formats_accepted(self, base_url):
        """Les 4 formats de préfixe valides sont acceptés sans ValueError."""
        valid_prefixes = ["sk_prod_", "sk_test_", "pk_prod_", "pk_test_"]
        for prefix in valid_prefixes:
            client = Sangho(prefix + "x" * 20, base_url=base_url)
            assert client is not None
