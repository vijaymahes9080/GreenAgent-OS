"""
Telemetry & Workloads API Endpoints for GreenAgent OS
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional, Dict, Any
from backend.app.core.data_contracts import ExecutionTrace, ExecutionStatus
from backend.app.services.profiler_service import ProfilerService
from backend.app.core.database import SessionLocal, WorkloadDB, ExecutionTraceDB
from backend.app.core.security import get_current_user

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("", response_model=Dict[str, Any])
async def submit_telemetry(payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    """Ingests external or manual telemetry from an agent execution."""
    trace = ProfilerService.record_telemetry(
        workload_id=payload.get("workload_id", "external-workload"),
        model=payload.get("model", "llama3.2:3b"),
        prompt_tokens=payload.get("prompt_tokens", 50),
        completion_tokens=payload.get("completion_tokens", 100),
        latency_ms=float(payload.get("latency_ms", 350.0)),
        retries=int(payload.get("retries", 0)),
        tool_calls_count=int(payload.get("tool_calls_count", 0)),
        cache_hit=bool(payload.get("cache_hit", False)),
        raw_response=payload.get("raw_response"),
        region=payload.get("region", "us-east"),
        measured_joules=payload.get("measured_joules")
    )
    return trace.model_dump()


@router.get("", response_model=List[Dict[str, Any]])
async def get_telemetry_history(
    limit: int = Query(50, ge=1, le=500),
    model: Optional[str] = None,
    workload_id: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieves paginated execution telemetry traces."""
    return ProfilerService.get_telemetry_traces(limit=limit, model=model, workload_id=workload_id)


# Workloads router
workloads_router = APIRouter(prefix="/workloads", tags=["workloads"])


@workloads_router.get("/{workload_id}")
async def get_workload_details(workload_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Fetches full execution trace and energy/carbon metrics for a specific workload ID."""
    db = SessionLocal()
    try:
        traces = db.query(ExecutionTraceDB).filter(ExecutionTraceDB.workload_id == workload_id).all()
        if not traces:
            raise HTTPException(status_code=404, detail=f"Workload '{workload_id}' not found")
        
        trace = traces[0]
        return {
            "workload_id": trace.workload_id,
            "model": trace.model,
            "status": trace.status,
            "latency_ms": trace.latency_ms,
            "total_tokens": trace.total_tokens,
            "energy_joules": trace.energy_joules,
            "carbon_co2e_grams": trace.carbon_co2e_grams,
            "measurement_method": trace.measurement_method,
            "timestamp": trace.timestamp.isoformat() if trace.timestamp else None,
            "cache_hit": trace.cache_hit
        }
    finally:
        db.close()
