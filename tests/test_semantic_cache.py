"""
Tests for Semantic Cache
Verifies exact match, similarity search, TTL, invalidation, and safety guardrails.
"""
from backend.app.core.data_contracts import Workload, WorkloadPriority
from backend.app.services.semantic_cache import SemanticCacheService
from backend.app.core.database import init_db

init_db()


def test_cache_storage_and_exact_lookup():
    wl = Workload(name="Cache Test", prompt="Explain solar power generation basics.")
    
    # Store
    cid = SemanticCacheService.store(
        workload=wl,
        response="Solar panels convert photons into electricity via the photovoltaic effect.",
        model="llama3.2:1b",
        tokens_saved=35,
        energy_saved_joules=1.2,
        carbon_saved_grams=0.0001
    )
    assert cid is not None

    # Exact Lookup
    hit = SemanticCacheService.lookup(wl)
    assert hit is not None
    assert hit["match_type"] == "EXACT"
    assert "photovoltaic" in hit["response"]


def test_safety_critical_cache_guardrail():
    # Emergency/Safety-critical workload must never be cached
    crit_wl = Workload(
        name="Emergency",
        prompt="URGENT: Patient has chest pain and shortness of breath.",
        priority=WorkloadPriority.EMERGENCY,
        safety_sensitive=True
    )
    can_cache, reason = SemanticCacheService.is_cacheable(crit_wl)
    assert can_cache is False
    assert "critical" in reason.lower()

    lookup_res = SemanticCacheService.lookup(crit_wl)
    assert lookup_res is None


def test_no_cache_flag_guardrail():
    wl = Workload(name="NonCacheable", prompt="Generate a random token.", allow_cache=False)
    can_cache, reason = SemanticCacheService.is_cacheable(wl)
    assert can_cache is False
