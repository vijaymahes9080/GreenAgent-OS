"""
Database Seed Script for GreenAgent OS
Populates initial sample telemetry traces and semantic cache entries for demonstration.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.database import init_db, SessionLocal, ExecutionTraceDB
from backend.app.core.data_contracts import Workload, WorkloadPriority
from backend.app.services.profiler_service import ProfilerService
from backend.app.services.semantic_cache import SemanticCacheService


def seed_data():
    print("Initializing database...")
    init_db()

    print("Seeding sample workloads & telemetry traces...")
    sample_workloads = [
        ("Summary-01", "Summarize Q3 financial revenue and operating income.", "llama3.2:1b", 80, 40, 190.0, False, "us-east"),
        ("SQL-02", "Write SQL query to extract monthly active users.", "llama3.2:3b", 60, 90, 310.0, False, "eu-north"),
        ("Reasoning-03", "Analyze distributed consensus failure modes in Raft.", "qwen2.5:14b", 120, 240, 950.0, False, "us-west"),
        ("CacheHit-04", "Explain the definition of grid carbon intensity.", "llama3.2:1b", 45, 60, 12.0, True, "us-east"),
        ("Medical-05", "EMERGENCY: Patient presenting with acute pulmonary embolism symptoms.", "mixtral:8x7b", 90, 180, 1420.0, False, "us-east"),
    ]

    for name, prompt, model, in_tok, out_tok, lat, cache_hit, reg in sample_workloads:
        ProfilerService.record_telemetry(
            workload_id=f"seed-{name.lower()}",
            model=model,
            prompt_tokens=in_tok,
            completion_tokens=out_tok,
            latency_ms=lat,
            cache_hit=cache_hit,
            region=reg,
            is_simulation=True
        )

    print("Seeding initial semantic cache entries...")
    cached_queries = [
        ("What is Power Usage Effectiveness PUE in datacenters?", "PUE is the ratio of total facility energy consumed to IT equipment energy consumed. An ideal PUE is 1.0.", "llama3.2:1b", 40, 1.4, 0.00015),
        ("How many Joules are in one Watt-hour?", "One Watt-hour is equivalent to exactly 3,600 Joules (1 Wh = 3600 J).", "llama3.2:1b", 30, 0.9, 0.00009),
    ]

    for q, ans, model, tok, j, carb in cached_queries:
        wl = Workload(name="SeedCache", prompt=q)
        SemanticCacheService.store(
            workload=wl,
            response=ans,
            model=model,
            tokens_saved=tok,
            energy_saved_joules=j,
            carbon_saved_grams=carb
        )

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_data()
