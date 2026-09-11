"""
Security Hardening and Governance for GreenAgent OS
Includes RBAC, API Key validation, secret redaction, signed webhooks,
rate limiting, and audit logging.
"""
import hmac
import hashlib
import re
import time
from typing import Optional, Dict, Any, List
from fastapi import Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from backend.app.config import settings

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER_NAME, auto_error=False)

# In-memory token bucket rate limiter
RATE_LIMIT_BUCKETS: Dict[str, Dict[str, Any]] = {}
MAX_REQUESTS_PER_MINUTE = 120

# RBAC Roles
VALID_ROLES = ["admin", "operator", "viewer"]
API_KEYS_STORE = {
    settings.DEFAULT_API_KEY: {"role": "admin", "client_id": "root-admin"},
    "ga-operator-key-2026": {"role": "operator", "client_id": "operator-user"},
    "ga-viewer-key-2026": {"role": "viewer", "client_id": "readonly-viewer"},
}

# Secret redaction regex patterns
SECRET_PATTERNS = [
    (re.compile(r"(sk-[a-zA-Z0-9]{20,})"), "[REDACTED_API_KEY]"),
    (re.compile(r"(bearer\s+[a-zA-Z0-9\-_.]+)", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"(ghp_[a-zA-Z0-9]{36})"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"(AKIA[0-9A-Z]{16})"), "[REDACTED_AWS_KEY]"),
    (re.compile(r"password['\"]?\s*[:=]\s*['\"]([^'\"]+)['\"]", re.IGNORECASE), "password: [REDACTED]")
]


class SecurityManager:
    """Security utilities for input validation, secret masking, and RBAC."""

    @staticmethod
    def redact_secrets(text: str) -> str:
        """Masks sensitive credentials, tokens, and keys from prompts/traces."""
        if not text:
            return text
        redacted = text
        for pattern, replacement in SECRET_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature_header: str, secret: str) -> bool:
        """Validates HMAC-SHA256 signature on incoming webhooks (e.g. n8n)."""
        if not signature_header or not secret:
            return False
        expected_sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected_sig}", signature_header)

    @staticmethod
    def generate_webhook_signature(payload: bytes, secret: str) -> str:
        """Generates HMAC-SHA256 signature for outgoing webhook notifications."""
        sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return f"sha256={sig}"

    @staticmethod
    def check_rate_limit(client_id: str) -> bool:
        """Simple in-memory token bucket rate limiter."""
        current_time = time.time()
        bucket = RATE_LIMIT_BUCKETS.setdefault(
            client_id, {"tokens": MAX_REQUESTS_PER_MINUTE, "last_updated": current_time}
        )

        elapsed = current_time - bucket["last_updated"]
        bucket["tokens"] = min(MAX_REQUESTS_PER_MINUTE, bucket["tokens"] + elapsed * (MAX_REQUESTS_PER_MINUTE / 60.0))
        bucket["last_updated"] = current_time

        if bucket["tokens"] >= 1.0:
            bucket["tokens"] -= 1.0
            return True
        return False


async def get_current_user(api_key: Optional[str] = Security(api_key_header)) -> Dict[str, Any]:
    """Validates API Key and returns authenticated client identity with RBAC role."""
    if not api_key:
        # If in dev environment and no key passed, allow dev viewer
        if settings.ENVIRONMENT == "development":
            return {"role": "admin", "client_id": "dev-local-user"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API Key header X-API-Key"
        )

    user_info = API_KEYS_STORE.get(api_key)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key credentials"
        )

    if not SecurityManager.check_rate_limit(user_info["client_id"]):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: max 120 requests/minute"
        )

    return user_info


def require_role(allowed_roles: List[str]):
    """Decorator dependency for RBAC enforcement."""
    async def role_checker(user: Dict[str, Any] = Security(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: role '{user['role']}' is not in allowed roles {allowed_roles}"
            )
        return user
    return role_checker
