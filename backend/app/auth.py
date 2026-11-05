import os
import time
import json
import base64
import hmac
import hashlib
import secrets
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db

# JWT Configuration & Secret Validation
KNOWN_DISALLOWED_JWT_PLACEHOLDERS = {
    "generate-a-secure-random-jwt-secret-key-here",
    "generate-a-secure-random-secret-key-here",
    "your_secure_random_secret_key_here",
    "your_super_secret_key_here_generate_with_openssl_rand_hex_32",
    "vote_guard_super_secure_jwt_secret_key_2026_change_in_prod",
    "change_this_to_a_secure_jwt_secret_key",
    "your_jwt_secret_key_here",
    "your_secret_key_here",
    "changeme",
    "secret",
}


def _resolve_jwt_secret() -> str:
    # 1. Primary: JWT_SECRET_KEY
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if jwt_secret is not None:
        jwt_secret_clean = jwt_secret.strip()
        if not jwt_secret_clean:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: 'JWT_SECRET_KEY' is empty or whitespace-only. "
                "The application cannot start without a valid cryptographic key for JWT signing."
            )
        if jwt_secret_clean.lower() in KNOWN_DISALLOWED_JWT_PLACEHOLDERS:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: The provided 'JWT_SECRET_KEY' is a known example placeholder. "
                "You must configure a unique, high-entropy cryptographic secret (at least 32 bytes) before starting the server. "
                "Example generator: openssl rand -hex 32"
            )
        if len(jwt_secret_clean.encode("utf-8")) < 32:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: The 'JWT_SECRET_KEY' is too weak. "
                "It must be at least 32 bytes (256 bits) in length for secure HMAC-SHA256 signing."
            )
        return jwt_secret_clean

    # 2. Legacy fallback: SECRET_KEY
    legacy_secret = os.getenv("SECRET_KEY")
    if legacy_secret is not None:
        legacy_clean = legacy_secret.strip()
        if not legacy_clean:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: 'SECRET_KEY' is empty or whitespace-only. "
                "The application cannot start without a valid cryptographic key."
            )
        if legacy_clean.lower() in {
            "generate-a-secure-random-jwt-secret-key-here",
            "your_secure_random_secret_key_here",
            "vote_guard_super_secure_jwt_secret_key_2026_change_in_prod",
            "your_super_secret_key_here_generate_with_openssl_rand_hex_32",
            "changeme",
            "secret",
        }:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: The provided 'SECRET_KEY' is a known example placeholder. "
                "Please configure a secure cryptographic secret (at least 32 bytes)."
            )
        if len(legacy_clean.encode("utf-8")) < 32:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: The 'SECRET_KEY' is too weak. "
                "It must be at least 32 bytes (256 bits) in length for secure HMAC-SHA256 signing."
            )
        return legacy_clean

    # 3. Neither key provided
    raise RuntimeError(
        "CRITICAL SECURITY CONFIGURATION ERROR: Neither 'JWT_SECRET_KEY' nor 'SECRET_KEY' is set in the environment. "
        "The application cannot start without a secure cryptographic key for JWT token signing. "
        "Please define 'JWT_SECRET_KEY' in your environment or 'backend/.env' file. "
        "Example generator: openssl rand -hex 32"
    )


JWT_SECRET_KEY = _resolve_jwt_secret()
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 60 * 60 * 12  # 12 hours

security = HTTPBearer(auto_error=False)


# ================= PASSWORD HASHING (PBKDF2-HMAC-SHA256) =================

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with 100,000 iterations and salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored PBKDF2 hash using constant-time comparison."""
    try:
        salt, key_hex = hashed_password.split("$", 1)
        test_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return secrets.compare_digest(test_key.hex(), key_hex)
    except Exception:
        return False


# ================= JWT GENERATION & VERIFICATION =================

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data_str: str) -> bytes:
    padding = "=" * (4 - (len(data_str) % 4)) if len(data_str) % 4 != 0 else ""
    return base64.urlsafe_b64decode((data_str + padding).encode("utf-8"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """Create an RFC 7519 compliant JWT using HMAC-SHA256."""
    to_encode = data.copy()
    expire = int(time.time()) + (expires_delta if expires_delta else JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})

    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(to_encode, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token. Raises HTTPException if invalid or expired."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed authentication token"
            )

        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        provided_sig = _base64url_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, provided_sig):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature"
            )

        payload = json.loads(_base64url_decode(payload_b64).decode("utf-8"))
        if "exp" in payload and int(time.time()) > payload["exp"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired. Please log in again."
            )

        return payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(exc)}"
        )


# ================= RBAC DEPENDENCIES =================

def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """
    FastAPI dependency that enforces admin role.
    Extracts Bearer JWT, validates token, and confirms user has role 'admin'.
    """
    from app.models import AdminUser

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required. Bearer token missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    username = payload.get("sub")
    role = payload.get("role")

    if not username or role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admin privilege required."
        )

    admin = db.query(AdminUser).filter(AdminUser.username == username, AdminUser.is_active == True).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account not found or inactive."
        )

    return admin
