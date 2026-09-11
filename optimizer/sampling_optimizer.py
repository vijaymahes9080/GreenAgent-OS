"""
Dynamic Sampling and Hyperparameter Tuner
Calibrates temperature, top-p, and max_tokens per task complexity tier to eliminate runaway token loops.
"""
from typing import Dict, Any
from backend.app.core.data_contracts import ComplexityLevel


class DynamicSamplingTuner:
    @staticmethod
    def get_optimal_sampling_params(complexity: ComplexityLevel, output_format: str = "text") -> Dict[str, Any]:
        """
        Structured or easy tasks use low temperature (greedy) to avoid extraneous tokens.
        Creative or hard reasoning tasks permit slightly higher variance.
        """
        if output_format in ["json", "sql", "code"] or complexity == ComplexityLevel.EASY:
            return {
                "temperature": 0.1,
                "top_p": 0.85,
                "max_tokens": 150,
                "repetition_penalty": 1.15,
                "rationale": "Greedy deterministic decoding prevents speculative token drift on structured/easy tasks"
            }
        elif complexity == ComplexityLevel.CRITICAL:
            return {
                "temperature": 0.0,
                "top_p": 1.0,
                "max_tokens": 300,
                "repetition_penalty": 1.1,
                "rationale": "Strict zero-temperature decoding mandated for safety-critical domain fidelity"
            }
        else:
            return {
                "temperature": 0.4,
                "top_p": 0.90,
                "max_tokens": 450,
                "repetition_penalty": 1.05,
                "rationale": "Balanced sampling for multi-step analytical reasoning"
            }
