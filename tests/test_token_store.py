"""
Tests for core.token_store.TokenStore
Run with: pytest tests/test_token_store.py -v
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from cryptography.fernet import Fernet

from core.token_store import TokenStore


@pytest.fixture
def master_key():
    """Generate a fresh Fernet key for each test."""
    return Fernet.generate_key().decode()


@pytest.fixture
def store(master_key, tmp_path):
    """Create a TokenStore backed by a temp file."""
    store_path = tmp_path / "test_tokens.json"
    return TokenStore(master_key=master_key, store_path=str(store_path))


class TestTokenStore:
    def test_save_and_get_credentials(self, store):
        store.save_credentials(
            owner_id="user1",
            provider="google",
            email="test@gmail.com",
            secret="refresh_token_abc123",
            meta={"host": "imap.gmail.com", "port": 993},
        )
        creds = store.get_credentials("user1")
        assert creds is not None
        assert creds["provider"] == "google"
        assert creds["email"] == "test@gmail.com"
        assert creds["secret"] == "refresh_token_abc123"
        assert creds["meta"]["host"] == "imap.gmail.com"

    def test_secret_is_encrypted_on_disk(self, store, tmp_path):
        store.save_credentials(
            owner_id="user1",
            provider="basic",
            email="test@example.com",
            secret="my_app_password",
        )
        # Read raw file — the secret should NOT appear in plaintext
        raw = (tmp_path / "test_tokens.json").read_text()
        assert "my_app_password" not in raw
        # But the email and provider are stored in plaintext
        assert "test@example.com" in raw
        assert "basic" in raw

    def test_get_nonexistent_owner(self, store):
        assert store.get_credentials("nonexistent") is None

    def test_delete_credentials(self, store):
        store.save_credentials("user1", "basic", "a@b.com", "pass123")
        assert store.has_credentials("user1")
        deleted = store.delete_credentials("user1")
        assert deleted is True
        assert store.get_credentials("user1") is None

    def test_delete_nonexistent(self, store):
        assert store.delete_credentials("nobody") is False

    def test_has_credentials(self, store):
        assert not store.has_credentials("user1")
        store.save_credentials("user1", "google", "x@y.com", "secret")
        assert store.has_credentials("user1")

    def test_overwrite_credentials(self, store):
        store.save_credentials("user1", "basic", "a@b.com", "old_pass")
        store.save_credentials("user1", "google", "a@b.com", "new_refresh_token")
        creds = store.get_credentials("user1")
        assert creds["provider"] == "google"
        assert creds["secret"] == "new_refresh_token"

    def test_multiple_owners(self, store):
        store.save_credentials("user1", "google", "a@g.com", "secret1")
        store.save_credentials("user2", "basic", "b@o.com", "secret2")
        c1 = store.get_credentials("user1")
        c2 = store.get_credentials("user2")
        assert c1["email"] == "a@g.com"
        assert c2["email"] == "b@o.com"

    def test_missing_master_key_raises(self):
        # Temporarily unset the env var
        old_val = os.environ.pop("TOKEN_MASTER_KEY", None)
        try:
            with pytest.raises(ValueError, match="TOKEN_MASTER_KEY"):
                TokenStore(master_key=None, store_path="/tmp/test.json")
        finally:
            if old_val:
                os.environ["TOKEN_MASTER_KEY"] = old_val

    def test_wrong_key_fails_decrypt(self, master_key, tmp_path):
        store_path = str(tmp_path / "test_tokens.json")
        store1 = TokenStore(master_key=master_key, store_path=store_path)
        store1.save_credentials("user1", "basic", "a@b.com", "secret")

        # Create a store with a different key
        other_key = Fernet.generate_key().decode()
        store2 = TokenStore(master_key=other_key, store_path=store_path)
        # Decryption should fail gracefully
        assert store2.get_credentials("user1") is None
