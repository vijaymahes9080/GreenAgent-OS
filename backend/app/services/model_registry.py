"""
Model Registry Service for GreenAgent OS
Maintains models, capabilities, cost, latency, energy baselines, and deterministic selection.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import uuid
from backend.app.core.data_contracts import ModelProfile, ComplexityLevel


class ModelRegistryService:
    """Manages available model profiles and deterministic rule-based selection."""

    # Pre-seeded open-source & local model catalog (CPU / zero-GPU friendly)
    _REGISTRY: Dict[str, ModelProfile] = {
        "llama3.2:1b": ModelProfile(
            name="llama3.2:1b",
            provider="ollama",
            capability_score=0.55,
            latency_estimate_ms=180.0,
            energy_estimate_j_per_token=0.035,
            cost_estimate_per_1k_tokens=0.0001,
            context_window=8192,
            availability=True,
            quality_benchmark={"gsm8k": 0.45, "mmlu": 0.49, "humaneval": 0.35},
            supported_complexity=[ComplexityLevel.EASY]
        ),
        "llama3.2:3b": ModelProfile(
            name="llama3.2:3b",
            provider="ollama",
            capability_score=0.72,
            latency_estimate_ms=320.0,
            energy_estimate_j_per_token=0.078,
            cost_estimate_per_1k_tokens=0.0003,
            context_window=8192,
            availability=True,
            quality_benchmark={"gsm8k": 0.62, "mmlu": 0.63, "humaneval": 0.52},
            supported_complexity=[ComplexityLevel.EASY, ComplexityLevel.MEDIUM]
        ),
        "mistral:7b": ModelProfile(
            name="mistral:7b",
            provider="ollama",
            capability_score=0.82,
            latency_estimate_ms=580.0,
            energy_estimate_j_per_token=0.185,
            cost_estimate_per_1k_tokens=0.0008,
            context_window=32768,
            availability=True,
            quality_benchmark={"gsm8k": 0.74, "mmlu": 0.71, "humaneval": 0.61},
            supported_complexity=[ComplexityLevel.EASY, ComplexityLevel.MEDIUM, ComplexityLevel.HARD]
        ),
        "llama3.1:8b": ModelProfile(
            name="llama3.1:8b",
            provider="ollama",
            capability_score=0.86,
            latency_estimate_ms=640.0,
            energy_estimate_j_per_token=0.210,
            cost_estimate_per_1k_tokens=0.0010,
            context_window=131072,
            availability=True,
            quality_benchmark={"gsm8k": 0.81, "mmlu": 0.77, "humaneval": 0.68},
            supported_complexity=[ComplexityLevel.EASY, ComplexityLevel.MEDIUM, ComplexityLevel.HARD]
        ),
        "qwen2.5:14b": ModelProfile(
            name="qwen2.5:14b",
            provider="ollama",
            capability_score=0.91,
            latency_estimate_ms=980.0,
            energy_estimate_j_per_token=0.390,
            cost_estimate_per_1k_tokens=0.0020,
            context_window=65536,
            availability=True,
            quality_benchmark={"gsm8k": 0.88, "mmlu": 0.84, "humaneval": 0.80},
            supported_complexity=[ComplexityLevel.MEDIUM, ComplexityLevel.HARD, ComplexityLevel.CRITICAL]
        ),
        "mixtral:8x7b": ModelProfile(
            name="mixtral:8x7b",
            provider="ollama",
            capability_score=0.94,
            latency_estimate_ms=1450.0,
            energy_estimate_j_per_token=0.540,
            cost_estimate_per_1k_tokens=0.0035,
            context_window=32768,
            availability=True,
            quality_benchmark={"gsm8k": 0.90, "mmlu": 0.87, "humaneval": 0.82},
            supported_complexity=[ComplexityLevel.HARD, ComplexityLevel.CRITICAL]
        ),
        "deepseek-r1:8b": ModelProfile(
            name="deepseek-r1:8b",
            provider="ollama",
            capability_score=0.89,
            latency_estimate_ms=750.0,
            energy_estimate_j_per_token=0.235,
            cost_estimate_per_1k_tokens=0.0012,
            context_window=65536,
            availability=True,
            quality_benchmark={"gsm8k": 0.89, "mmlu": 0.80, "humaneval": 0.76},
            supported_complexity=[ComplexityLevel.MEDIUM, ComplexityLevel.HARD, ComplexityLevel.CRITICAL]
        ),
    }

    @classmethod
    def list_models(cls) -> List[ModelProfile]:
        """Returns all registered models."""
        return list(cls._REGISTRY.values())

    @classmethod
    def get_model(cls, model_name: str) -> Optional[ModelProfile]:
        """Retrieves a specific model profile."""
        return cls._REGISTRY.get(model_name)

    @classmethod
    def register_model(cls, profile: ModelProfile) -> ModelProfile:
        """Registers or updates a model profile."""
        cls._REGISTRY[profile.name] = profile
        return profile

    @classmethod
    def select_deterministic_model(
        cls,
        complexity: ComplexityLevel,
        min_quality: float = 0.70,
        max_latency_ms: float = 5000.0,
        prefer_efficiency: bool = True
    ) -> ModelProfile:
        """
        Deterministic model selector choosing the most energy-efficient model
        that satisfies complexity tier, quality floor, and latency constraints.
        """
        candidates = [
            m for m in cls._REGISTRY.values()
            if m.availability and
               complexity in m.supported_complexity and
               m.capability_score >= min_quality and
               m.latency_estimate_ms <= max_latency_ms
        ]

        if not candidates:
            # Fallback to strongest available model if constraints are too tight
            sorted_by_power = sorted(cls._REGISTRY.values(), key=lambda m: m.capability_score, reverse=True)
            return sorted_by_power[0]

        if prefer_efficiency:
            # Sort by lowest energy consumption first, then lowest cost
            candidates.sort(key=lambda m: (m.energy_estimate_j_per_token, m.cost_estimate_per_1k_tokens))
        else:
            # Sort by highest capability
            candidates.sort(key=lambda m: m.capability_score, reverse=True)

        return candidates[0]
