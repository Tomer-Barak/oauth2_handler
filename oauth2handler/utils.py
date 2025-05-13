"""
OAuth2 Handler Utilities
"""
import os
import json
import hashlib
import base64
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Constants
TOKEN_DIR = "tokens"


def ensure_token_dir():
    """Ensure the token directory exists."""
    os.makedirs(TOKEN_DIR, exist_ok=True)


def get_token_file(service_name: str) -> str:
    """Get the path to the token file for a service."""
    return os.path.join(TOKEN_DIR, f"token_{service_name}.json")


def save_token(service_name: str, data: Dict[str, Any]) -> None:
    """Save token data to a file."""
    ensure_token_dir()
    data["timestamp"] = datetime.utcnow().isoformat()
    with open(get_token_file(service_name), "w") as f:
        json.dump(data, f)


def load_token(service_name: str) -> Optional[Dict[str, Any]]:
    """Load token data from a file."""
    token_path = get_token_file(service_name)
    if not os.path.exists(token_path):
        return None
    with open(token_path, "r") as f:
        data = json.load(f)
    return data


def is_token_expired(token_data: Dict[str, Any], buffer_seconds: int = 60) -> bool:
    """Check if a token is expired."""
    if "expires_in" not in token_data or "timestamp" not in token_data:
        return True
    
    issued_at = datetime.fromisoformat(token_data["timestamp"])
    expires_in = int(token_data["expires_in"])
    return datetime.utcnow() >= issued_at + timedelta(seconds=expires_in - buffer_seconds)


def generate_pkce_challenge() -> Dict[str, str]:
    """Generate PKCE code verifier and challenge.
    
    Returns:
        Dict with code_verifier and code_challenge
    """
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    
    return {
        "code_verifier": code_verifier,
        "code_challenge": code_challenge
    }


def load_config_file(config_file: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to load config file {config_file}: {e}")
