"""
Prometheus Metrics Exporter for GreenAgent OS
Exposes OpenTelemetry and Prometheus compliant gauges and counters at /metrics.
"""
from fastapi import APIRouter, Response
from backend.app.core.database import SessionLocal, ExecutionTraceDB, CacheEntryDB

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def get_prometheus_metrics():
    """Outputs Prometheus formatted gauge & counter metrics."""
    db = SessionLocal()
    try:
        traces = db.query(ExecutionTraceDB).all()
        cache_entries = db.query(CacheEntryDB).all()

        total_joules = sum(t.energy_joules or 0.0 for t in traces)
        total_carbon = sum(t.carbon_co2e_grams or 0.0 for t in traces)
        total_hits = sum(c.hit_count for c in cache_entries)
        total_saved_joules = sum((c.energy_saved_joules or 0.0) * c.hit_count for c in cache_entries)

        content = (
            "# HELP greenagent_energy_joules_total Total electrical energy consumed by AI workloads in Joules\n"
            "# TYPE greenagent_energy_joules_total counter\n"
            f"greenagent_energy_joules_total {total_joules:.3f}\n\n"
            "# HELP greenagent_carbon_grams_total Total greenhouse gas emissions emitted in grams CO2e\n"
            "# TYPE greenagent_carbon_grams_total counter\n"
            f"greenagent_carbon_grams_total {total_carbon:.5f}\n\n"
            "# HELP greenagent_cache_hits_total Total semantic cache hits eliminating inference\n"
            "# TYPE greenagent_cache_hits_total counter\n"
            f"greenagent_cache_hits_total {total_hits}\n\n"
            "# HELP greenagent_energy_saved_joules_total Total Joules avoided via caching and routing\n"
            "# TYPE greenagent_energy_saved_joules_total counter\n"
            f"greenagent_energy_saved_joules_total {total_saved_joules:.3f}\n"
        )
        return Response(content=content, media_type="text/plain; version=0.0.4")
    finally:
        db.close()
