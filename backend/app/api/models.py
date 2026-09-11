"""
Model Registry API Endpoints for GreenAgent OS
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from backend.app.core.data_contracts import ModelProfile, ComplexityLevel
from backend.app.services.model_registry import ModelRegistryService
from backend.app.core.security import get_current_user, require_role

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=List[ModelProfile])
async def list_models(user: Dict[str, Any] = Depends(get_current_user)):
    """Lists all available model profiles with energy, latency, and capability specs."""
    return ModelRegistryService.list_models()


@router.post("", response_model=ModelProfile)
async def register_model(
    profile: ModelProfile,
    user: Dict[str, Any] = Depends(require_role(["admin"]))
):
    """Registers or updates a model profile in the registry (Admin only)."""
    return ModelRegistryService.register_model(profile)


@router.post("/select", response_model=ModelProfile)
async def select_model_deterministically(
    payload: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Selects the optimal model profile deterministically based on
    task complexity tier, quality floor, and latency requirements.
    """
    complexity_str = payload.get("complexity", "MEDIUM").upper()
    complexity = getattr(ComplexityLevel, complexity_str, ComplexityLevel.MEDIUM)
    min_quality = float(payload.get("min_quality", 0.70))
    max_latency = float(payload.get("max_latency_ms", 5000.0))
    prefer_efficiency = bool(payload.get("prefer_efficiency", True))

    selected = ModelRegistryService.select_deterministic_model(
        complexity=complexity,
        min_quality=min_quality,
        max_latency_ms=max_latency,
        prefer_efficiency=prefer_efficiency
    )
    return selected
