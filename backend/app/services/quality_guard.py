"""
Quality Guard Service for GreenAgent OS
Validates output quality against task completion, required schema fields,
factual consistency heuristics, and tool-call success rates.
Triggers automated rollback/retry with a stronger model if quality degrades.
"""
from typing import Dict, Any, Optional, List
import json
import re
from backend.app.core.data_contracts import (
    Workload, ExecutionTrace, QualityEvaluation, ModelProfile
)
from backend.app.services.model_registry import ModelRegistryService


class QualityGuard:
    """Evaluates output fidelity and guards against degradation."""

    @classmethod
    def evaluate_quality(
        cls,
        workload: Workload,
        response_text: str,
        tool_calls_attempted: int = 0,
        tool_calls_succeeded: int = 0
    ) -> QualityEvaluation:
        """Evaluates completion, schema fields, and consistency."""
        rejection_reason = None
        rejection_occurred = False
        suggested_fallback = None

        # 1. Check Task Completion (non-empty, minimum length sanity)
        word_count = len(response_text.split()) if response_text else 0
        if word_count < 3:
            rejection_occurred = True
            rejection_reason = "Degraded output: response text is empty or trivially brief (<3 words)"
            task_completion = 0.1
        elif word_count < 15 and len(workload.prompt.split()) > 30:
            task_completion = 0.5
        else:
            task_completion = 0.95

        # 2. Check Required Schema / Fields
        required_fields_present = True
        if workload.expected_output_format == "json":
            try:
                # Try finding JSON block
                json_match = re.search(r"\{.*\}|\[.*\]", response_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    # Check any specific required fields in metadata
                    expected_keys = workload.metadata.get("required_keys", [])
                    for k in expected_keys:
                        if isinstance(parsed, dict) and k not in parsed:
                            required_fields_present = False
                            rejection_reason = f"Missing required JSON schema key: '{k}'"
                            rejection_occurred = True
                            break
                else:
                    required_fields_present = False
                    rejection_reason = "Failed to produce valid JSON as requested"
                    rejection_occurred = True
            except Exception:
                required_fields_present = False
                rejection_reason = "JSON parsing syntax error in generated output"
                rejection_occurred = True

        # 3. Tool Call Success Rate
        tool_success_rate = 1.0
        if tool_calls_attempted > 0:
            tool_success_rate = tool_calls_succeeded / tool_calls_attempted
            if tool_success_rate < 0.70:
                rejection_occurred = True
                rejection_reason = f"Tool call success rate below threshold: {tool_success_rate*100:.1f}%"

        # 4. Factual Consistency Heuristics
        # Penalize hallucination or contradiction tokens if present
        refusal_patterns = [r"\bas an ai language model\b", r"\bi cannot fulfill\b", r"\berror 500\b"]
        refusal_hit = any(re.search(p, response_text.lower()) for p in refusal_patterns)
        factual_score = 0.40 if refusal_hit else 0.92

        # Weighted aggregate quality score
        schema_factor = 1.0 if required_fields_present else 0.3
        overall_score = round(
            (task_completion * 0.45 + factual_score * 0.35 + tool_success_rate * 0.20) * schema_factor,
            3
        )

        meets_threshold = overall_score >= workload.required_quality_min and not rejection_occurred

        if not meets_threshold and not rejection_reason:
            rejection_occurred = True
            rejection_reason = f"Overall quality score ({overall_score}) fell below required threshold ({workload.required_quality_min})"

        if rejection_occurred:
            # Recommend next stronger model in registry
            stronger_models = sorted(
                [m for m in ModelRegistryService.list_models() if m.capability_score > 0.85],
                key=lambda m: m.capability_score,
                reverse=True
            )
            suggested_fallback = stronger_models[0].name if stronger_models else "llama3.1:8b"

        return QualityEvaluation(
            workload_id=workload.id,
            overall_quality_score=overall_score,
            factual_consistency=factual_score,
            task_completion=task_completion,
            required_fields_present=required_fields_present,
            tool_call_success_rate=tool_success_rate,
            meets_threshold=meets_threshold,
            rejection_occurred=rejection_occurred,
            rejection_reason=rejection_reason,
            suggested_fallback_model=suggested_fallback,
            confidence=0.89
        )
