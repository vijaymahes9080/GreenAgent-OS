"""
Tests for Model Registry and Deterministic Selection
"""
from backend.app.core.data_contracts import ComplexityLevel, ModelProfile
from backend.app.services.model_registry import ModelRegistryService


def test_list_models():
    models = ModelRegistryService.list_models()
    assert len(models) >= 5
    names = [m.name for m in models]
    assert "llama3.2:1b" in names
    assert "mixtral:8x7b" in names


def test_deterministic_model_selection():
    # Easy complexity with high latency allowance should select lowest energy model
    easy_model = ModelRegistryService.select_deterministic_model(
        complexity=ComplexityLevel.EASY,
        min_quality=0.50,
        max_latency_ms=3000.0,
        prefer_efficiency=True
    )
    assert easy_model.name in ["llama3.2:1b", "llama3.2:3b"]

    # Critical complexity must select high-capability model
    crit_model = ModelRegistryService.select_deterministic_model(
        complexity=ComplexityLevel.CRITICAL,
        min_quality=0.88,
        max_latency_ms=5000.0
    )
    assert crit_model.capability_score >= 0.88
