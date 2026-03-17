"""
TRIDENT Token Store
Encrypted credential/token storage using Fernet symmetric encryption.
Persists to data/tokens.json with secrets encrypted at rest.
"""
import json
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

# Default storage path relative to project root
_DEFAULT_STORE_PATH = Path(__file__).resolve().parent.parent / "data" / "tokens.json"


class TokenStore:
    """
    Encrypted credential store backed by a JSON file.

    Each entry is keyed by ``owner_id`` and stores:
        provider  – "google" | "microsoft" | "basic"
        email     – the mailbox email address
        secret    – **encrypted** app-password or refresh-token JSON
        meta      – optional plaintext metadata dict (host, port, etc.)
    """

    def __init__(
        self,
        master_key: Optional[str] = None,
        store_path: Optional[str] = None,
    ):
        key = master_key or os.environ.get("TOKEN_MASTER_KEY")
        if not key:
            raise ValueError(
                "TOKEN_MASTER_KEY must be provided or set as an environment variable. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
        self._path = Path(store_path) if store_path else _DEFAULT_STORE_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> Dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            logger.warning("token store file corrupt or unreadable – starting fresh")
            return {}

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def _encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def _decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_credentials(
        self,
        owner_id: str,
        provider: str,
        email: str,
        secret: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store credentials for *owner_id*, encrypting *secret* at rest."""
        data = self._load()
        data[owner_id] = {
            "provider": provider,
            "email": email,
            "encrypted_secret": self._encrypt(secret),
            "meta": meta or {},
        }
        self._save(data)
        logger.info("saved credentials for owner_id=%s provider=%s", owner_id, provider)

    def get_credentials(self, owner_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt credentials for *owner_id*.

        Returns a dict with keys ``provider``, ``email``, ``secret`` (decrypted),
        and ``meta``, or ``None`` if not found.
        """
        data = self._load()
        entry = data.get(owner_id)
        if entry is None:
            return None
        try:
            decrypted_secret = self._decrypt(entry["encrypted_secret"])
        except (InvalidToken, KeyError):
            logger.error("failed to decrypt secret for owner_id=%s", owner_id)
            return None
        return {
            "provider": entry["provider"],
            "email": entry["email"],
            "secret": decrypted_secret,
            "meta": entry.get("meta", {}),
        }

    def delete_credentials(self, owner_id: str) -> bool:
        """Delete stored credentials for *owner_id*. Returns True if deleted."""
        data = self._load()
        if owner_id not in data:
            return False
        del data[owner_id]
        self._save(data)
        logger.info("deleted credentials for owner_id=%s", owner_id)
        return True

    def has_credentials(self, owner_id: str) -> bool:
        """Check whether credentials exist for *owner_id* without decrypting."""
        data = self._load()
        return owner_id in data
