"""
Cache Management API Endpoints for GreenAgent OS
"""
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.app.core.database import SessionLocal, CacheEntryDB
from backend.app.services.semantic_cache import SemanticCacheService
from backend.app.core.security import get_current_user, require_role

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("", response_model=Dict[str, Any])
async def get_cache_stats(limit: int = Query(50, ge=1, le=500), user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves cache entries, aggregated savings, and hit telemetry."""
    db = SessionLocal()
    try:
        now_utc = datetime.now(timezone.utc)
        now_naive = datetime.utcnow()
        entries = db.query(CacheEntryDB).order_by(CacheEntryDB.hit_count.desc()).limit(limit).all()

        total_hits = sum(e.hit_count for e in entries)
        total_tokens_saved = sum(e.tokens_saved * e.hit_count for e in entries)
        total_joules_saved = sum(e.energy_saved_joules * e.hit_count for e in entries)
        total_carbon_saved = sum(e.carbon_saved_grams * e.hit_count for e in entries)

        def check_expired(exp) -> bool:
            if not exp:
                return False
            comp = now_utc if exp.tzinfo is not None else now_naive
            return exp < comp

        serialized = [
            {
                "id": e.id,
                "key_hash": e.key_hash,
                "prompt_snippet": e.prompt[:80] + ("..." if len(e.prompt) > 80 else ""),
                "model": e.model,
                "tokens_saved": e.tokens_saved,
                "energy_saved_joules": e.energy_saved_joules,
                "carbon_saved_grams": e.carbon_saved_grams,
                "hit_count": e.hit_count,
                "expires_at": e.expires_at.isoformat() if e.expires_at else None,
                "is_expired": check_expired(e.expires_at)
            }
            for e in entries
        ]

        return {
            "total_entries": len(entries),
            "aggregate_hits": total_hits,
            "total_tokens_saved": total_tokens_saved,
            "total_joules_saved": round(total_joules_saved, 2),
            "total_co2e_grams_saved": round(total_carbon_saved, 4),
            "entries": serialized
        }
    finally:
        db.close()


@router.post("/invalidate")
async def invalidate_cache(
    payload: Optional[Dict[str, Any]] = None,
    user: Dict[str, Any] = Depends(require_role(["admin", "operator"]))
):
    """Invalidates specific key hash or cleans expired entries."""
    key_hash = payload.get("key_hash") if payload else None
    deleted_count = SemanticCacheService.invalidate(key_hash)
    return {"status": "SUCCESS", "deleted_entries": deleted_count}
