"""
Semantic Cache Service for GreenAgent OS
Provides exact and embedding-based similarity lookup, provenance tracking,
TTL invalidation, and safety guards against caching critical/volatile data.
"""
import hashlib
import time
import json
import re
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime, timezone, timedelta
import numpy as np

from backend.app.core.data_contracts import CacheEntry, Workload, WorkloadPriority
from backend.app.core.database import SessionLocal, CacheEntryDB
from backend.app.config import settings

# Optional sentence transformer embedding model fallback to TF-IDF / character n-gram cosine
_EMBED_MODEL = None


def get_embedding_vector(text: str) -> List[float]:
    """
    Computes a normalized dense vector for semantic similarity.
    Uses a fast deterministic n-gram and token hashing vectorizer (128-dim).
    """
    words = re.findall(r"\w+", text.lower())
    vec = np.zeros(128, dtype=np.float32)
    for w in words:
        # Unigram hash
        idx = int(hashlib.md5(w.encode()).hexdigest(), 16) % 128
        vec[idx] += 1.0
        # Bigrams / subwords
        if len(w) >= 4:
            b_idx = int(hashlib.md5(w[:4].encode()).hexdigest(), 16) % 128
            vec[b_idx] += 0.5
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec.tolist()


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class SemanticCacheService:
    """Manages semantic caching with strict safety guards and provenance."""

    @staticmethod
    def is_cacheable(workload: Workload) -> Tuple[bool, Optional[str]]:
        """
        Guardrails enforcing prompt policy:
        Do not cache:
        - Safety-critical or emergency workloads
        - Requests explicitly marked non-cacheable
        - Volatile/dynamic queries (e.g. current time, stock ticker, live weather)
        """
        if not workload.allow_cache:
            return False, "Cache explicitly disallowed in workload policy"

        if workload.safety_sensitive or workload.priority in [WorkloadPriority.CRITICAL, WorkloadPriority.EMERGENCY]:
            return False, "Safety-critical / emergency workloads bypass cache to guarantee fresh reasoning"

        # Check for volatile keywords
        volatile_patterns = [r"\bnow\b", r"\btoday\b", r"\bcurrent\s+time\b", r"\blive\s+stock\b", r"\brandom\b"]
        for pat in volatile_patterns:
            if re.search(pat, workload.prompt, re.IGNORECASE):
                return False, f"Volatile/time-dependent pattern detected: {pat}"

        return True, None

    @classmethod
    def lookup(
        cls,
        workload: Workload,
        similarity_threshold: float = settings.CACHE_SIMILARITY_THRESHOLD
    ) -> Optional[Dict[str, Any]]:
        """
        Looks up prompt in semantic cache.
        Checks exact hash first, then searches embedding similarity.
        """
        can_cache, reason = cls.is_cacheable(workload)
        if not can_cache:
            return None

        clean_prompt = workload.prompt.strip()
        exact_hash = hashlib.sha256(clean_prompt.encode()).hexdigest()

        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)

            # 1. Exact match
            exact_match = db.query(CacheEntryDB).filter(
                CacheEntryDB.key_hash == exact_hash,
                CacheEntryDB.expires_at > now
            ).first()

            if exact_match:
                exact_match.hit_count += 1
                db.commit()
                return {
                    "cache_id": exact_match.id,
                    "response": exact_match.response,
                    "model": exact_match.model,
                    "match_type": "EXACT",
                    "similarity": 1.0,
                    "tokens_saved": exact_match.tokens_saved,
                    "energy_saved_joules": exact_match.energy_saved_joules,
                    "carbon_saved_grams": exact_match.carbon_saved_grams,
                }

            # 2. Semantic vector match
            query_vec = get_embedding_vector(clean_prompt)
            candidates = db.query(CacheEntryDB).filter(CacheEntryDB.expires_at > now).all()

            best_match = None
            best_sim = 0.0

            for cand in candidates:
                if not cand.embedding_json:
                    continue
                cand_vec = json.loads(cand.embedding_json)
                sim = cosine_similarity(query_vec, cand_vec)
                if sim > best_sim and sim >= similarity_threshold:
                    best_sim = sim
                    best_match = cand

            if best_match:
                best_match.hit_count += 1
                db.commit()
                return {
                    "cache_id": best_match.id,
                    "response": best_match.response,
                    "model": best_match.model,
                    "match_type": "SEMANTIC",
                    "similarity": round(best_sim, 4),
                    "tokens_saved": best_match.tokens_saved,
                    "energy_saved_joules": best_match.energy_saved_joules,
                    "carbon_saved_grams": best_match.carbon_saved_grams,
                }

            return None
        finally:
            db.close()

    @classmethod
    def store(
        cls,
        workload: Workload,
        response: str,
        model: str,
        tokens_saved: int,
        energy_saved_joules: float,
        carbon_saved_grams: float,
        ttl_seconds: int = settings.CACHE_DEFAULT_TTL_SECONDS
    ) -> Optional[str]:
        """Stores a completed workload result into the semantic cache with provenance metadata."""
        can_cache, _ = cls.is_cacheable(workload)
        if not can_cache:
            return None

        clean_prompt = workload.prompt.strip()
        key_hash = hashlib.sha256(clean_prompt.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

        embedding = get_embedding_vector(clean_prompt)

        db = SessionLocal()
        try:
            # Check existing entry
            existing = db.query(CacheEntryDB).filter(CacheEntryDB.key_hash == key_hash).first()
            if existing:
                existing.response = response
                existing.expires_at = expires_at
                existing.tokens_saved = tokens_saved
                existing.energy_saved_joules = energy_saved_joules
                existing.carbon_saved_grams = carbon_saved_grams
                db.commit()
                return existing.id

            new_entry = CacheEntryDB(
                id=f"cache_{hashlib.md5(key_hash.encode()).hexdigest()[:12]}",
                key_hash=key_hash,
                prompt=clean_prompt,
                response=response,
                model=model,
                tokens_saved=tokens_saved,
                energy_saved_joules=energy_saved_joules,
                carbon_saved_grams=carbon_saved_grams,
                ttl_seconds=ttl_seconds,
                expires_at=expires_at,
                hit_count=0,
                safety_tier="general",
                embedding_json=json.dumps(embedding)
            )
            db.add(new_entry)
            db.commit()
            return new_entry.id
        except Exception:
            db.rollback()
            return None
        finally:
            db.close()

    @staticmethod
    def invalidate(key_hash: Optional[str] = None) -> int:
        """Invalidates specific cache key or all expired entries."""
        db = SessionLocal()
        try:
            if key_hash:
                count = db.query(CacheEntryDB).filter(CacheEntryDB.key_hash == key_hash).delete()
            else:
                now = datetime.now(timezone.utc)
                count = db.query(CacheEntryDB).filter(CacheEntryDB.expires_at <= now).delete()
            db.commit()
            return count
        finally:
            db.close()
