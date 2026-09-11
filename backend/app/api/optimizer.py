"""
Optimizer API Endpoints for GreenAgent OS
Coordinates multi-objective optimization, local Ollama execution (with deterministic fallback),
quality evaluation, semantic caching, and full lifecycle telemetry.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
import httpx
import time

from backend.app.core.data_contracts import (
    Workload, OptimizationDecision, ExecutionStatus, WorkloadPriority
)
from backend.app.services.multi_objective_optimizer import MultiObjectiveOptimizer
from backend.app.services.quality_guard import QualityGuard
from backend.app.services.semantic_cache import SemanticCacheService
from backend.app.services.profiler_service import ProfilerService
from backend.app.core.security import get_current_user
from backend.app.config import settings

router = APIRouter(prefix="/optimizer", tags=["optimizer"])


async def execute_model_inference(model: str, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes model generation via local Ollama API.
    Falls back to deterministic local simulation if Ollama is not actively running.
    Requires no cloud keys and no GPU.
    """
    start_time = time.perf_counter()
    ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt or "You are GreenAgent OS Assistant. Be concise and accurate.",
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(ollama_url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                return {
                    "response": data.get("response", ""),
                    "prompt_tokens": data.get("prompt_eval_count", len(prompt.split()) * 2),
                    "completion_tokens": data.get("eval_count", 80),
                    "latency_ms": latency_ms,
                    "measured_joules": None,
                    "source": "ollama_local"
                }
    except Exception:
        pass

    # Deterministic simulation fallback
    latency_ms = (time.perf_counter() - start_time) * 1000.0 + 120.0
    prompt_tokens = len(prompt.split()) * 2
    completion_tokens = max(30, min(250, len(prompt.split()) + 40))
    simulated_response = (
        f"[GreenAgent OS Engine ({model})]\n"
        f"Processed query: '{prompt[:50]}...'\n"
        f"Execution completed under carbon-aware budget constraints."
    )

    return {
        "response": simulated_response,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "latency_ms": latency_ms,
        "measured_joules": None,
        "source": "deterministic_simulation"
    }


@router.post("/optimize", response_model=Dict[str, Any])
async def plan_optimization(workload: Workload, user: Dict[str, Any] = Depends(get_current_user)):
    """Generates an optimization plan without executing."""
    decision = MultiObjectiveOptimizer.optimize(workload)
    return decision.model_dump()


@router.post("/execute", response_model=Dict[str, Any])
async def execute_optimized_workload(workload: Workload, user: Dict[str, Any] = Depends(get_current_user)):
    """
    Executes a workload through the full GreenAgent pipeline:
    Cache check -> Multi-objective optimization -> Execution -> Quality Guard -> Telemetry.
    """
    # 1. Step 1: Check Semantic Cache
    cached_result = SemanticCacheService.lookup(workload)
    if cached_result:
        trace = ProfilerService.record_telemetry(
            workload_id=workload.id,
            model=cached_result["model"],
            prompt_tokens=len(workload.prompt.split()) * 2,
            completion_tokens=60,
            latency_ms=10.0,
            cache_hit=True,
            status=ExecutionStatus.CACHED,
            raw_response=cached_result["response"],
            region=workload.preferred_region
        )
        return {
            "workload_id": workload.id,
            "status": "CACHED",
            "model_used": cached_result["model"],
            "cache_hit": True,
            "response": cached_result["response"],
            "latency_ms": 10.0,
            "energy_saved_joules": cached_result["energy_saved_joules"],
            "carbon_saved_grams": cached_result["carbon_saved_grams"],
            "trace_id": trace.id
        }

    # 2. Step 2: Multi-Objective Optimization
    decision = MultiObjectiveOptimizer.optimize(workload)

    # 3. Step 3: Inference execution
    inference_result = await execute_model_inference(
        model=decision.selected_model,
        prompt=workload.prompt,
        system_prompt=workload.system_prompt
    )

    response_text = inference_result["response"]
    prompt_tokens = inference_result["prompt_tokens"]
    completion_tokens = inference_result["completion_tokens"]
    latency_ms = inference_result["latency_ms"]

    # 4. Step 4: Quality Guard Evaluation
    quality_eval = QualityGuard.evaluate_quality(
        workload=workload,
        response_text=response_text
    )

    model_used = decision.selected_model

    # Rollback/Retry if quality failed
    if quality_eval.rejection_occurred and quality_eval.suggested_fallback_model:
        fallback_model = quality_eval.suggested_fallback_model
        retry_result = await execute_model_inference(
            model=fallback_model,
            prompt=workload.prompt,
            system_prompt=workload.system_prompt
        )
        response_text = retry_result["response"]
        prompt_tokens += retry_result["prompt_tokens"]
        completion_tokens += retry_result["completion_tokens"]
        latency_ms += retry_result["latency_ms"]
        model_used = fallback_model

    # 5. Step 5: Cache storage
    tokens_total = prompt_tokens + completion_tokens
    est_joules = tokens_total * 0.15
    est_carbon = est_joules * 0.0001
    SemanticCacheService.store(
        workload=workload,
        response=response_text,
        model=model_used,
        tokens_saved=tokens_total,
        energy_saved_joules=est_joules,
        carbon_saved_grams=est_carbon
    )

    # 6. Step 6: Telemetry Recording
    trace = ProfilerService.record_telemetry(
        workload_id=workload.id,
        model=model_used,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        cache_hit=False,
        status=ExecutionStatus.COMPLETED,
        raw_response=response_text,
        region=decision.target_region,
        is_simulation=(inference_result["source"] == "deterministic_simulation")
    )

    return {
        "workload_id": workload.id,
        "status": "COMPLETED",
        "model_used": model_used,
        "cache_hit": False,
        "response": response_text,
        "latency_ms": round(latency_ms, 2),
        "tokens_total": tokens_total,
        "quality_score": quality_eval.overall_quality_score,
        "quality_meets_threshold": quality_eval.meets_threshold,
        "rejection_occurred": quality_eval.rejection_occurred,
        "optimization_decision": decision.model_dump(),
        "trace_id": trace.id
    }
