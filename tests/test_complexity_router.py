"""
Tests for Task Complexity Router
"""
from backend.app.core.data_contracts import Workload, ComplexityLevel, WorkloadPriority
from backend.app.services.complexity_router import ComplexityRouter


def test_classify_easy_task():
    wl = Workload(name="Easy", prompt="What is the capital of France?")
    comp, reasons, conf = ComplexityRouter.classify_complexity(wl)
    assert comp == ComplexityLevel.EASY
    assert conf > 0.85


def test_classify_code_and_reasoning_task():
    wl = Workload(
        name="Hard Reasoning",
        prompt="Prove and analyze step-by-step why QuickSort has average O(n log n) runtime using recursion trees."
    )
    comp, reasons, conf = ComplexityRouter.classify_complexity(wl)
    assert comp in [ComplexityLevel.MEDIUM, ComplexityLevel.HARD]


def test_classify_critical_task():
    wl = Workload(
        name="Medical Emergency",
        prompt="Patient is in anaphylactic shock. Calculate immediate epinephrine dose.",
        priority=WorkloadPriority.CRITICAL,
        safety_sensitive=True
    )
    comp, reasons, conf = ComplexityRouter.classify_complexity(wl)
    assert comp == ComplexityLevel.CRITICAL
    assert conf >= 0.95
