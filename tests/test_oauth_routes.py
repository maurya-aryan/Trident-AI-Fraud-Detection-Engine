"""
Tests for OAuth/mailbox connect API routes.
Run with: pytest tests/test_oauth_routes.py -v
"""
import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from cryptography.fernet import Fernet


# We need TOKEN_MASTER_KEY set before importing routes
_TEST_KEY = Fernet.generate_key().decode()
_TEST_STORE_DIR = tempfile.mkdtemp()

os.environ.setdefault("TOKEN_MASTER_KEY", _TEST_KEY)


from fastapi.testclient import TestClient
from api.routes import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def _patch_token_store(tmp_path):
    """Ensure each test uses an isolated token store."""
    store_path = str(tmp_path / "test_tokens.json")

    def _make_store():
        from core.token_store import TokenStore
        return TokenStore(master_key=_TEST_KEY, store_path=store_path)

    with patch("api.routes._get_token_store", _make_store):
        yield _make_store


class TestConnectBasic:
    def test_stores_credentials(self, client, _patch_token_store):
        resp = client.post("/connect/basic", json={
            "owner_id": "test1",
            "email": "user@example.com",
            "host": "imap.example.com",
            "password": "app_password_123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["email"] == "user@example.com"

        # Verify stored via token store
        store = _patch_token_store()
        creds = store.get_credentials("test1")
        assert creds is not None
        assert creds["provider"] == "basic"
        assert creds["secret"] == "app_password_123"

    def test_requires_email(self, client):
        resp = client.post("/connect/basic", json={
            "password": "abc",
        })
        assert resp.status_code == 422  # Validation error


class TestAuthDisconnect:
    def test_disconnect_existing(self, client, _patch_token_store):
        # First store something
        store = _patch_token_store()
        store.save_credentials("test1", "basic", "a@b.com", "pass")

        resp = client.post("/auth/disconnect", params={"owner_id": "test1"})
        assert resp.status_code == 200
        assert resp.json()["deleted"] is True

    def test_disconnect_nonexistent(self, client):
        resp = client.post("/auth/disconnect", params={"owner_id": "nobody"})
        assert resp.status_code == 200
        assert resp.json()["deleted"] is False


class TestConnectTest:
    def test_no_stored_credentials(self, client):
        resp = client.post("/poller/connect-test", params={"owner_id": "nobody"})
        assert resp.status_code == 404

    @patch("api.routes.imaplib")
    def test_basic_connect_success(self, mock_imaplib, client, _patch_token_store):
        # Store basic creds
        store = _patch_token_store()
        store.save_credentials("test1", "basic", "a@b.com", "pass", {"host": "imap.test.com", "port": 993})

        # Mock IMAP
        mock_conn = MagicMock()
        mock_conn.select.return_value = ("OK", [b"42"])
        mock_imaplib.IMAP4_SSL.return_value = mock_conn

        resp = client.post("/poller/connect-test", params={"owner_id": "test1"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["inbox_count"] == 42
        assert data["provider"] == "basic"


class TestGoogleOAuthStart:
    def test_start_without_client_id(self, client):
        """If GOOGLE_CLIENT_ID is not set, should return 500."""
        with patch("api.auth_google.GOOGLE_CLIENT_ID", ""):
            resp = client.get("/auth/google/start", params={"owner_id": "test1"})
            assert resp.status_code == 500

    def test_start_with_client_id(self, client):
        """If GOOGLE_CLIENT_ID is set, should return auth_url."""
        with patch("api.auth_google.GOOGLE_CLIENT_ID", "fake-client-id"):
            resp = client.get(
                "/auth/google/start",
                params={"owner_id": "test1", "redirect_frontend": "http://localhost:5173"},
                follow_redirects=False,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "auth_url" in data
            assert "accounts.google.com" in data["auth_url"]
            assert "fake-client-id" in data["auth_url"]
