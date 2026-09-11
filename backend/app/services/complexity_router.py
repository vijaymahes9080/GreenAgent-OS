"""
Task Complexity Router for GreenAgent OS
Classifies incoming workload complexity (EASY, MEDIUM, HARD, CRITICAL)
using deterministic heuristics first, then routes to an appropriate model.
"""
from typing import Dict, Any, List, Tuple
import re
from backend.app.core.data_contracts import (
    Workload, ComplexityLevel, WorkloadPriority, ModelProfile
)
from backend.app.services.model_registry import ModelRegistryService


# Heuristic Regex Indicators
REASONING_PATTERNS = [
    r"\bprove\b", r"\bcalculate\b", r"\bderive\b", r"\banalyze\b",
    r"\barchitecture\b", r"\bdiagnose\b", r"\boptimize\b", r"\bstep[- ]by[- ]step\b",
    r"\broot[- ]cause\b", r"\bquantum\b", r"\brecursion\b"
]

CODE_PATTERNS = [
    r"```[a-zA-Z]*", r"\bdef\s+\w+", r"\bclass\s+\w+", r"\bfunction\s*\(",
    r"\bSELECT\s+.+\s+FROM\b", r"\bJOIN\b", r"\bSQL\b", r"\brefactor\b"
]

CRITICAL_DOMAINS = [
    r"\bpatient\b", r"\bmedical\b", r"\bdiagnosis\b", r"\blegal\s+liability\b",
    r"\bemergency\b", r"\bproduction\s+down\b", r"\bsecurity\s+vulnerability\b",
    r"\bzero[- ]day\b", r"\bheart\s+rate\b", r"\bflight\s+control\b"
]


class ComplexityRouter:
    """Deterministic-first complexity analyzer and model selector."""

    @classmethod
    def classify_complexity(cls, workload: Workload) -> Tuple[ComplexityLevel, List[str], float]:
        """
        Evaluates task complexity through deterministic signals.
        Returns: (ComplexityLevel, List[reasoning_strings], confidence)
        """
        reasons = []
        prompt = workload.prompt.lower()
        word_count = len(workload.prompt.split())

        # 1. Check CRITICAL overrides first
        if workload.safety_sensitive or workload.priority in [WorkloadPriority.CRITICAL, WorkloadPriority.EMERGENCY]:
            reasons.append("Explicit workload priority or safety-sensitive flag marked as CRITICAL/EMERGENCY")
            return ComplexityLevel.CRITICAL, reasons, 0.99

        for crit in CRITICAL_DOMAINS:
            if re.search(crit, prompt):
                reasons.append(f"Safety-critical domain keyword match: '{crit}'")
                return ComplexityLevel.CRITICAL, reasons, 0.95

        # 2. Heuristic scoring
        complexity_score = 0.0

        # Context Size
        if word_count > 1200:
            complexity_score += 2.5
            reasons.append(f"Large prompt context ({word_count} words)")
        elif word_count > 400:
            complexity_score += 1.2
            reasons.append(f"Medium prompt context ({word_count} words)")
        else:
            reasons.append(f"Concise prompt context ({word_count} words)")

        # Reasoning requirements
        reasoning_hits = sum(1 for p in REASONING_PATTERNS if re.search(p, prompt))
        if reasoning_hits >= 3:
            complexity_score += 2.5
            reasons.append(f"High multi-step reasoning requirement ({reasoning_hits} analytical keywords)")
        elif reasoning_hits >= 1:
            complexity_score += 1.0
            reasons.append(f"Analytical reasoning signal detected ({reasoning_hits} keyword)")

        # Code / Structured Output
        code_hits = sum(1 for p in CODE_PATTERNS if re.search(p, workload.prompt))
        if code_hits > 0 or workload.expected_output_format in ["json", "sql", "code"]:
            complexity_score += 1.5
            reasons.append(f"Structured syntax/code generation requirement ({workload.expected_output_format})")

        # Tool Requirements
        tool_reqs = workload.metadata.get("tools_required", [])
        if len(tool_reqs) >= 2:
            complexity_score += 2.0
            reasons.append(f"Multi-tool coordination needed ({len(tool_reqs)} tools)")
        elif len(tool_reqs) == 1:
            complexity_score += 1.0
            reasons.append("Single external tool invocation required")

        # Previous failure rate penalty
        prev_failure_rate = workload.metadata.get("previous_failure_rate", 0.0)
        if prev_failure_rate > 0.25:
            complexity_score += 1.5
            reasons.append(f"Elevated historical failure rate on similar tasks ({prev_failure_rate*100:.1f}%)")

        # Determine level from cumulative score
        if complexity_score >= 4.5:
            level = ComplexityLevel.HARD
            confidence = 0.88
        elif complexity_score >= 2.0:
            level = ComplexityLevel.MEDIUM
            confidence = 0.90
        else:
            level = ComplexityLevel.EASY
            confidence = 0.94

        return level, reasons, confidence

    @classmethod
    def route_workload(cls, workload: Workload) -> Dict[str, Any]:
        """
        Classifies complexity and selects the best model.
        Returns a complete routing decision packet.
        """
        complexity, reasons, confidence = cls.classify_complexity(workload)

        # Select deterministic model based on complexity and constraints
        selected_model = ModelRegistryService.select_deterministic_model(
            complexity=complexity,
            min_quality=workload.required_quality_min,
            max_latency_ms=workload.deadline_seconds * 1000.0,
            prefer_efficiency=True
        )

        return {
            "complexity": complexity,
            "selected_model": selected_model.name,
            "model_provider": selected_model.provider,
            "capability_score": selected_model.capability_score,
            "estimated_j_per_token": selected_model.energy_estimate_j_per_token,
            "reasons": reasons,
            "confidence": confidence
        }
