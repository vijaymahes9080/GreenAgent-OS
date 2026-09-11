"""
Tests for Multi-Objective Optimizer
"""
from backend.app.core.data_contracts import Workload, ComplexityLevel
from backend.app.services.multi_objective_optimizer import MultiObjectiveOptimizer
from backend.app.core.database import init_db

init_db()


def test_optimizer_decision_structure():
    wl = Workload(
        name="Opt Test",
        prompt="Write a Python script to sort a list of numbers.",
        required_quality_min=0.80
    )
    decision = MultiObjectiveOptimizer.optimize(wl)

    assert decision.selected_model is not None
    assert decision.target_region in ["us-east", "us-west", "eu-central", "eu-north", "ap-south"]
    assert decision.optimization_objective_value >= 0.0
    assert "alpha" in decision.weights_applied
    assert len(decision.rationale) >= 2


def test_optimizer_respects_quality_floor():
    wl = Workload(
        name="High Quality Mandate",
        prompt="Draft a complex legal contract clause.",
        required_quality_min=0.90
    )
    decision = MultiObjectiveOptimizer.optimize(wl)
    assert decision.predicted_quality_score >= 0.90
