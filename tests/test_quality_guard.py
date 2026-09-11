"""
Tests for Quality Guard
"""
from backend.app.core.data_contracts import Workload
from backend.app.services.quality_guard import QualityGuard


def test_quality_guard_passes_good_output():
    wl = Workload(name="Task", prompt="Explain photosynthesis.")
    eval_res = QualityGuard.evaluate_quality(
        workload=wl,
        response_text="Photosynthesis is the biological process converting light into chemical energy.",
        tool_calls_attempted=1,
        tool_calls_succeeded=1
    )
    assert eval_res.meets_threshold is True
    assert eval_res.rejection_occurred is False


def test_quality_guard_rejects_empty_output():
    wl = Workload(name="Task", prompt="Explain quantum entanglement.")
    eval_res = QualityGuard.evaluate_quality(
        workload=wl,
        response_text="ok"
    )
    assert eval_res.rejection_occurred is True
    assert eval_res.suggested_fallback_model is not None


def test_quality_guard_rejects_missing_json_keys():
    wl = Workload(
        name="JSON Task",
        prompt="Output JSON with status and count",
        expected_output_format="json",
        metadata={"required_keys": ["count"]}
    )
    # Output missing "count"
    eval_res = QualityGuard.evaluate_quality(
        workload=wl,
        response_text='{"status": "ok"}'
    )
    assert eval_res.rejection_occurred is True
    assert "count" in eval_res.rejection_reason
