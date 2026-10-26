"""
Authentication Service for SmartSilageAI (SIH26111)
Handles password hashing and token generation cleanly.
"""
import hashlib
import hmac
import os
import time
from typing import Optional, Dict, Any

SECRET_KEY = os.getenv("SECRET_KEY", "sih26111_secret_key_change_in_production_dairy_2026")


def hash_password(password: str) -> str:
    """Computes SHA-256 hash with salt for secure local storage."""
    salt = "sih26111_salt_secure"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored hash."""
    return hash_password(plain_password) == hashed_password


def create_access_token(farmer_id: int, mobile: str) -> str:
    """
    Creates a simple token encoding farmer_id and mobile.
    Format: farmer_id:mobile:timestamp:signature
    """
    timestamp = int(time.time())
    payload = f"{farmer_id}:{mobile}:{timestamp}"
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def verify_token(token: str) -> Optional[int]:
    """
    Verifies token validity and returns the farmer_id.
    """
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return None
        farmer_id, mobile, timestamp, sig = parts
        payload = f"{farmer_id}:{mobile}:{timestamp}"
        expected_sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        
        if hmac.compare_digest(sig, expected_sig):
            # Check expiration (24 hours = 86400 seconds)
            if time.time() - int(timestamp) < 86400:
                return int(farmer_id)
        return None
    except Exception:
        return None
