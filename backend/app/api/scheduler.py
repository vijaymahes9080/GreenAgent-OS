"""
Scheduler API Endpoints for GreenAgent OS
Exposes regional grid intensity and temporal scheduling actions.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from datetime import datetime, timezone

from backend.app.core.data_contracts import Workload, SchedulingDecision
from backend.app.core.carbon_intensity import CarbonCalculator, REGIONAL_CARBON_PROFILES
from backend.app.services.scheduler_service import CarbonAwareScheduler
from backend.app.core.security import get_current_user

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/regions", response_model=List[Dict[str, Any]])
async def list_regions_carbon(user: Dict[str, Any] = Depends(get_current_user)):
    """Returns all supported datacenter regions with current carbon intensity and 24h forecast."""
    results = []
    current_hour = datetime.now(timezone.utc).hour

    for region_id, prof in REGIONAL_CARBON_PROFILES.items():
        intensity_now = CarbonCalculator.get_grid_intensity(region_id, current_hour)
        hourly_forecast = [
            {"hour": h, "intensity_g_kwh": CarbonCalculator.get_grid_intensity(region_id, h)}
            for h in range(24)
        ]
        results.append({
            "region_id": region_id,
            "region_name": prof["region_name"],
            "country": prof["country"],
            "current_intensity_g_kwh": intensity_now,
            "datacenter_pue": prof["datacenter_pue"],
            "forecast_24h": hourly_forecast
        })

    return results


@router.post("/schedule", response_model=Dict[str, Any])
async def schedule_task(workload: Workload, user: Dict[str, Any] = Depends(get_current_user)):
    """Computes carbon-aware scheduling decision (EXECUTE_NOW, DELAY, MOVE_REGION)."""
    decision = CarbonAwareScheduler.schedule_workload(
        workload=workload,
        estimated_energy_joules=15.0,
        current_region=workload.preferred_region
    )
    return decision.model_dump()
