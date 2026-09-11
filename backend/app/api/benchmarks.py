"""
Benchmarks API Endpoints for GreenAgent OS
Allows triggering and viewing 100-workload sustainability comparisons.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import json
from pathlib import Path

from backend.app.core.security import get_current_user
from benchmarks.run_benchmark import run_benchmark

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.get("/latest", response_model=Dict[str, Any])
async def get_latest_benchmark(user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves the most recent benchmark run results."""
    res_file = Path(__file__).resolve().parent.parent.parent.parent / "benchmarks" / "benchmark_results.json"
    if res_file.exists():
        with open(res_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # If not yet executed, run and return
    result = run_benchmark()
    return result.model_dump()


@router.post("/run", response_model=Dict[str, Any])
async def execute_benchmark_suite(user: Dict[str, Any] = Depends(get_current_user)):
    """Executes the full 100-workload benchmark comparison live."""
    result = run_benchmark()
    return result.model_dump()
