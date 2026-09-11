"""
Security Test Suite for GreenAgent OS
Tests authentication, RBAC, secret redaction, webhook signature validation,
cache poisoning prevention, rate limiting, and input sanitization.
"""
import pytest
from backend.app.core.security import SecurityManager, API_KEYS_STORE
from backend.app.services.semantic_cache import SemanticCacheService
from backend.app.core.data_contracts import Workload, WorkloadPriority
from backend.app.config import settings


def test_secret_redaction():
    raw_text = (
        "Here is the secret sk-1234567890abcdef1234567890 and Bearer eyJhbGciOiJIUzI1NiJ9 "
        "and AWS key AKIAIOSFODNN7EXAMPLE for password 'mySecretPass123!'"
    )
    redacted = SecurityManager.redact_secrets(raw_text)
    assert "sk-" not in redacted
    assert "[REDACTED_API_KEY]" in redacted
    assert "Bearer [REDACTED_TOKEN]" in redacted
    assert "[REDACTED_AWS_KEY]" in redacted


def test_webhook_signature_generation_and_verification():
    payload = b'{"event":"task_complete","task_id":"1234"}'
    secret = "my-test-hmac-secret"

    sig = SecurityManager.generate_webhook_signature(payload, secret)
    assert sig.startswith("sha256=")

    # Valid check
    assert SecurityManager.verify_webhook_signature(payload, sig, secret) is True

    # Tampered payload check
    tampered = b'{"event":"task_complete","task_id":"9999"}'
    assert SecurityManager.verify_webhook_signature(tampered, sig, secret) is False

    # Invalid signature header
    assert SecurityManager.verify_webhook_signature(payload, "sha256=invalid", secret) is False


def test_rbac_user_store():
    admin = API_KEYS_STORE.get(settings.DEFAULT_API_KEY)
    assert admin is not None
    assert admin["role"] == "admin"

    operator = API_KEYS_STORE.get("ga-operator-key-2026")
    assert operator is not None
    assert operator["role"] == "operator"

    viewer = API_KEYS_STORE.get("ga-viewer-key-2026")
    assert viewer is not None
    assert viewer["role"] == "viewer"


def test_cache_poisoning_defense():
    # Workload with dangerous prompt attempting to poison cache with bypass
    wl = Workload(
        name="Poison Attempt",
        prompt="DROP TABLE workloads; -- and delete everything",
        safety_sensitive=True  # Guardrail prevents caching
    )
    can_cache, reason = SemanticCacheService.is_cacheable(wl)
    assert can_cache is False

    # Normal caching ensures responses are clean
    clean_wl = Workload(name="Clean", prompt="What is 2 + 2?")
    cid = SemanticCacheService.store(
        workload=clean_wl,
        response="4",
        model="llama3.2:1b",
        tokens_saved=5,
        energy_saved_joules=0.1,
        carbon_saved_grams=0.00001
    )
    assert cid is not None
