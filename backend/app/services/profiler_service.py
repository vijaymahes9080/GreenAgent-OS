"""
Profiler Service for GreenAgent OS
Tracks execution telemetry, model calls, latency, tool calls, and orchestrates
energy and carbon estimations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import json
from backend.app.core.data_contracts import (
    ExecutionTrace, ExecutionStatus, EnergyEstimate, CarbonEstimate, MeasurementMethod
)
from backend.app.core.energy_estimator import EnergyEstimator
from backend.app.core.carbon_intensity import CarbonCalculator
from backend.app.core.database import SessionLocal, ExecutionTraceDB, WorkloadDB
from backend.app.core.security import SecurityManager


class ProfilerService:
    """Telemetry collection and profiling coordinator."""

    @staticmethod
    def record_telemetry(
        workload_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        retries: int = 0,
        tool_calls_count: int = 0,
        tool_calls_latency_ms: float = 0.0,
        cache_hit: bool = False,
        status: ExecutionStatus = ExecutionStatus.COMPLETED,
        raw_response: Optional[str] = None,
        region: str = "us-east",
        measured_joules: Optional[float] = None,
        is_simulation: bool = False,
        error_message: Optional[str] = None
    ) -> ExecutionTrace:
        """
        Records an execution trace, computes energy and carbon metrics,
        redacts sensitive fields, and stores in the database.
        """
        # 1. Sanitize & redact secrets from raw response
        sanitized_response = SecurityManager.redact_secrets(raw_response) if raw_response else None

        # 2. Compute Energy Estimate (Joules, Wh)
        duration_seconds = latency_ms / 1000.0
        energy_est = EnergyEstimator.estimate_energy(
            workload_id=workload_id,
            model=model,
            tokens_input=prompt_tokens,
            tokens_output=completion_tokens,
            duration_seconds=duration_seconds,
            measured_joules=measured_joules,
            is_simulation=is_simulation
        )

        # 3. Compute Carbon Estimate (CO2e grams)
        carbon_est = CarbonCalculator.calculate_carbon(
            workload_id=workload_id,
            energy_joules=energy_est.joules,
            region=region,
            is_simulation=is_simulation
        )

        trace = ExecutionTrace(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="1.0.0",
            source="greenagent-profiler",
            workload_id=workload_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=round(latency_ms, 2),
            retries=retries,
            tool_calls_count=tool_calls_count,
            tool_calls_latency_ms=round(tool_calls_latency_ms, 2),
            cache_hit=cache_hit,
            status=status,
            raw_response=sanitized_response,
            energy_estimate=energy_est,
            carbon_estimate=carbon_est,
            error_message=error_message
        )

        # 4. Persist to DB
        db = SessionLocal()
        try:
            db_record = ExecutionTraceDB(
                id=trace.id,
                workload_id=trace.workload_id,
                model=trace.model,
                prompt_tokens=trace.prompt_tokens,
                completion_tokens=trace.completion_tokens,
                total_tokens=trace.total_tokens,
                latency_ms=trace.latency_ms,
                retries=trace.retries,
                tool_calls_count=trace.tool_calls_count,
                tool_calls_latency_ms=trace.tool_calls_latency_ms,
                cache_hit=trace.cache_hit,
                status=trace.status.value,
                raw_response=trace.raw_response,
                energy_joules=energy_est.joules,
                carbon_co2e_grams=carbon_est.estimated_co2e_grams,
                measurement_method=energy_est.method.value,
                details_json=json.dumps({
                    "energy_details": energy_est.details,
                    "carbon_intensity_g_kwh": carbon_est.grid_intensity_g_per_kwh,
                    "region": carbon_est.grid_region,
                    "confidence_energy": energy_est.confidence,
                    "confidence_carbon": carbon_est.confidence
                })
            )
            db.add(db_record)
            db.commit()
        except Exception as ex:
            db.rollback()
        finally:
            db.close()

        return trace

    @staticmethod
    def get_telemetry_traces(
        limit: int = 50,
        model: Optional[str] = None,
        workload_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries telemetry traces with optional model and workload filtering."""
        db = SessionLocal()
        try:
            query = db.query(ExecutionTraceDB)
            if model:
                query = query.filter(ExecutionTraceDB.model == model)
            if workload_id:
                query = query.filter(ExecutionTraceDB.workload_id == workload_id)
            records = query.order_by(ExecutionTraceDB.timestamp.desc()).limit(limit).all()
            
            results = []
            for r in records:
                results.append({
                    "id": r.id,
                    "workload_id": r.workload_id,
                    "model": r.model,
                    "prompt_tokens": r.prompt_tokens,
                    "completion_tokens": r.completion_tokens,
                    "total_tokens": r.total_tokens,
                    "latency_ms": r.latency_ms,
                    "retries": r.retries,
                    "tool_calls_count": r.tool_calls_count,
                    "cache_hit": r.cache_hit,
                    "status": r.status,
                    "energy_joules": r.energy_joules,
                    "carbon_co2e_grams": r.carbon_co2e_grams,
                    "measurement_method": r.measurement_method,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                    "details": json.loads(r.details_json) if r.details_json else {}
                })
            return results
        finally:
            db.close()
