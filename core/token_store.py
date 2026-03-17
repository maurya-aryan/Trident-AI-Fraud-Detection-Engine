import json
import os
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any

# Path to store the tokens
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tokens.json')

def _get_fernet() -> Fernet:
    """Gets the Fernet instance using TOKEN_MASTER_KEY from environment."""
    key = os.environ.get('TOKEN_MASTER_KEY')
    if not key:
        raise ValueError("TOKEN_MASTER_KEY environment variable is not set. It must be a 32-byte Fernet key.")
    try:
        return Fernet(key.encode())
    except Exception as e:
        raise ValueError(f"Invalid TOKEN_MASTER_KEY: {e}")

def _load_tokens() -> Dict[str, Any]:
    """Loads tokens from the JSON file."""
    if not os.path.exists(TOKEN_FILE):
        return {}
    try:
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_tokens(tokens: Dict[str, Any]):
    """Saves tokens to the JSON file, locking file permissions to owner."""
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=4)
    # Set permissions to read/write for owner only (600)
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except Exception:
        pass

def save_credentials(owner_id: str, provider: str, email: str, secret: str, meta: Optional[Dict] = None):
    """
    Encrypts and saves credentials for an owner.
    
    Args:
        owner_id: Unique identifier for the owner/mailbox.
        provider: 'google', 'microsoft', or 'basic'.
        email: The email address.
        secret: The refresh token or app password.
        meta: Optional metadata.
    """
    f = _get_fernet()
    encrypted_secret = f.encrypt(secret.encode()).decode()
    
    tokens = _load_tokens()
    tokens[owner_id] = {
        'provider': provider,
        'email': email,
        'secret': encrypted_secret,
        'meta': meta or {}
    }
    _save_tokens(tokens)

def get_credentials(owner_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves and decrypts credentials for an owner.
    
    Returns:
        Dict with 'provider', 'email', 'secret' (decrypted), 'meta'
        or None if not found.
    """
    tokens = _load_tokens()
    if owner_id not in tokens:
        return None
        
    data = tokens[owner_id]
    f = _get_fernet()
    try:
        decrypted_secret = f.decrypt(data['secret'].encode()).decode()
        return {
            'provider': data['provider'],
            'email': data['email'],
            'secret': decrypted_secret,
            'meta': data.get('meta', {})
        }
    except Exception as e:
        # Transparent error for decryption failure (e.g. key changed)
        raise ValueError(f"Failed to decrypt credentials for {owner_id}. Key might be invalid: {e}")

def delete_credentials(owner_id: str):
    """Deletes credentials for an owner."""
    tokens = _load_tokens()
    if owner_id in tokens:
        del tokens[owner_id]
        _save_tokens(tokens)
