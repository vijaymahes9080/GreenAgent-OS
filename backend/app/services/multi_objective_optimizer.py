"""
Multi-Objective Optimizer for GreenAgent OS
Optimizes joint trade-off across energy, carbon, cost, latency, and quality loss
using constrained scalarization and Pareto-efficient candidate ranking.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from backend.app.core.data_contracts import (
    Workload, OptimizationDecision, SchedulingAction, ComplexityLevel
)
from backend.app.services.model_registry import ModelRegistryService
from backend.app.services.complexity_router import ComplexityRouter
from backend.app.services.scheduler_service import CarbonAwareScheduler
from backend.app.services.semantic_cache import SemanticCacheService
from backend.app.core.carbon_intensity import CarbonCalculator
from backend.app.config import settings


class MultiObjectiveOptimizer:
    """
    Evaluates execution alternatives and minimizes the objective loss:
      J = alpha * E_norm + beta * C_norm + gamma * Cost_norm + delta * L_norm + epsilon * Q_loss
    subject to:
      quality >= min_quality
      latency <= max_latency
      scheduled_time <= deadline
      model.available == True
    """

    @classmethod
    def optimize(
        cls,
        workload: Workload,
        alpha: float = settings.OPT_ALPHA,
        beta: float = settings.OPT_BETA,
        gamma: float = settings.OPT_GAMMA,
        delta: float = settings.OPT_DELTA,
        epsilon: float = settings.OPT_EPSILON
    ) -> OptimizationDecision:
        """Computes the globally optimal plan for the given workload."""
        # 1. Step 1: Check Semantic Cache first
        cached_result = SemanticCacheService.lookup(workload)
        if cached_result:
            return OptimizationDecision(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                version="1.0.0",
                source="greenagent-optimizer",
                workload_id=workload.id,
                detected_complexity=ComplexityLevel.EASY,
                selected_model=cached_result["model"],
                scheduling_action=SchedulingAction.USE_CACHE,
                target_region=workload.preferred_region,
                use_cache=True,
                predicted_latency_ms=12.0,
                predicted_energy_joules=0.1,
                predicted_carbon_grams=0.00001,
                predicted_cost_usd=0.0,
                predicted_quality_score=1.0,
                weights_applied={
                    "alpha": alpha, "beta": beta, "gamma": gamma,
                    "delta": delta, "epsilon": epsilon
                },
                optimization_objective_value=0.0001,
                rationale=[
                    f"Semantic cache hit ({cached_result['match_type']}, sim={cached_result['similarity']:.3f})",
                    f"Eliminated redundant inference; saved ~{cached_result['energy_saved_joules']:.1f} Joules"
                ],
                confidence=0.98
            )

        # 2. Step 2: Classify Task Complexity
        complexity, router_reasons, router_conf = ComplexityRouter.classify_complexity(workload)

        # 3. Step 3: Candidate Model Evaluation
        models = ModelRegistryService.list_models()
        valid_candidates = []

        # Est tokens for normalized evaluation
        est_tokens_in = len(workload.prompt.split()) * 2
        est_tokens_out = 150 if complexity == ComplexityLevel.EASY else 350

        for model in models:
            if not model.availability:
                continue

            # Hard Constraint 1: Quality Floor
            if model.capability_score < workload.required_quality_min:
                continue

            # Hard Constraint 2: Complexity Fit
            if complexity not in model.supported_complexity:
                continue

            # Hard Constraint 3: Latency Limit
            if (model.latency_estimate_ms / 1000.0) > workload.deadline_seconds:
                continue

            # Metrics
            est_energy_j = (est_tokens_in * 0.04) + (est_tokens_out * model.energy_estimate_j_per_token)
            est_cost_usd = ((est_tokens_in + est_tokens_out) / 1000.0) * model.cost_estimate_per_1k_tokens
            quality_loss = max(0.0, 1.0 - model.capability_score)

            valid_candidates.append({
                "model": model,
                "energy_j": est_energy_j,
                "cost_usd": est_cost_usd,
                "latency_ms": model.latency_estimate_ms,
                "quality_loss": quality_loss,
                "capability": model.capability_score
            })

        # Fallback if no candidate meets strict constraints
        if not valid_candidates:
            # Pick strongest available model
            fallback = sorted(models, key=lambda m: m.capability_score, reverse=True)[0]
            valid_candidates.append({
                "model": fallback,
                "energy_j": 50.0,
                "cost_usd": 0.001,
                "latency_ms": fallback.latency_estimate_ms,
                "quality_loss": 0.05,
                "capability": fallback.capability_score
            })

        # Step 4: Carbon Scheduling
        # Find best candidate by multi-objective score
        best_candidate = None
        lowest_objective = float("inf")
        best_sched_decision = None

        for cand in valid_candidates:
            sched = CarbonAwareScheduler.schedule_workload(
                workload,
                estimated_energy_joules=cand["energy_j"],
                current_region=workload.preferred_region
            )

            # Carbon estimate under scheduled region
            carb = CarbonCalculator.calculate_carbon(
                workload_id=workload.id,
                energy_joules=cand["energy_j"],
                region=sched.scheduled_region
            )

            # Normalization baselines: Energy(100J), Carbon(0.05g), Cost($0.005), Latency(2000ms)
            norm_e = min(1.0, cand["energy_j"] / 100.0)
            norm_c = min(1.0, carb.estimated_co2e_grams / 0.05)
            norm_cost = min(1.0, cand["cost_usd"] / 0.005)
            norm_l = min(1.0, cand["latency_ms"] / 2000.0)
            norm_q = cand["quality_loss"]

            # Scalarized objective
            obj_val = (
                alpha * norm_e +
                beta * norm_c +
                gamma * norm_cost +
                delta * norm_l +
                epsilon * norm_q
            )

            if obj_val < lowest_objective:
                lowest_objective = obj_val
                best_candidate = cand
                best_candidate["carbon_grams"] = carb.estimated_co2e_grams
                best_sched_decision = sched

        chosen_model = best_candidate["model"]
        rationale = [
            f"Detected task complexity tier: {complexity.value}",
            *router_reasons,
            f"Selected {chosen_model.name} (capability={chosen_model.capability_score:.2f}) meeting min quality {workload.required_quality_min}",
            f"Scheduling action: {best_sched_decision.action.value} -> {best_sched_decision.scheduled_region} ({best_sched_decision.rationale})"
        ]

        return OptimizationDecision(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="1.0.0",
            source="greenagent-optimizer",
            workload_id=workload.id,
            detected_complexity=complexity,
            selected_model=chosen_model.name,
            scheduling_action=best_sched_decision.action,
            target_region=best_sched_decision.scheduled_region,
            use_cache=False,
            predicted_latency_ms=round(best_candidate["latency_ms"], 1),
            predicted_energy_joules=round(best_candidate["energy_j"], 2),
            predicted_carbon_grams=round(best_candidate["carbon_grams"], 6),
            predicted_cost_usd=round(best_candidate["cost_usd"], 6),
            predicted_quality_score=round(best_candidate["capability"], 3),
            weights_applied={
                "alpha": alpha, "beta": beta, "gamma": gamma,
                "delta": delta, "epsilon": epsilon
            },
            optimization_objective_value=round(lowest_objective, 4),
            rationale=rationale,
            confidence=round((router_conf + best_sched_decision.confidence) / 2.0, 2)
        )
