"""
Tests for Profiler and Energy Estimator
Ensures distinction between measured, estimated, and simulated metrics.
"""
from backend.app.core.data_contracts import MeasurementMethod, ExecutionStatus
from backend.app.core.energy_estimator import EnergyEstimator
from backend.app.core.carbon_intensity import CarbonCalculator
from backend.app.services.profiler_service import ProfilerService
from backend.app.core.database import init_db

init_db()


def test_energy_estimator_methods():
    # 1. Measured Energy
    est_measured = EnergyEstimator.estimate_energy(
        workload_id="test-1",
        model="llama3.2:1b",
        tokens_input=100,
        tokens_output=100,
        duration_seconds=1.0,
        measured_joules=12.5
    )
    assert est_measured.method == MeasurementMethod.MEASURED_ENERGY
    assert est_measured.joules == 12.5

    # 2. Parametric Model Estimate
    est_model = EnergyEstimator.estimate_energy(
        workload_id="test-2",
        model="mistral:7b",
        tokens_input=100,
        tokens_output=100,
        duration_seconds=1.0
    )
    assert est_model.method == MeasurementMethod.ESTIMATED_ENERGY
    assert est_model.joules > 0.0
    assert "active_joules" in est_model.details

    # 3. Simulated Estimate
    est_sim = EnergyEstimator.estimate_energy(
        workload_id="test-3",
        model="llama3.1:8b",
        tokens_input=100,
        tokens_output=100,
        duration_seconds=1.0,
        is_simulation=True
    )
    assert est_sim.method == MeasurementMethod.SIMULATED_CARBON


def test_carbon_calculator_diurnal_curve():
    # Midday solar peak intensity (lower) vs midnight thermal base (higher)
    intensity_noon = CarbonCalculator.get_grid_intensity("us-east", hour_of_day=12)
    intensity_midnight = CarbonCalculator.get_grid_intensity("us-east", hour_of_day=0)
    assert intensity_noon <= intensity_midnight


def test_profiler_telemetry_recording():
    trace = ProfilerService.record_telemetry(
        workload_id="test-prof-1",
        model="llama3.2:3b",
        prompt_tokens=40,
        completion_tokens=80,
        latency_ms=250.0,
        cache_hit=False,
        status=ExecutionStatus.COMPLETED
    )
    assert trace.id is not None
    assert trace.energy_estimate is not None
    assert trace.carbon_estimate is not None
    assert trace.latency_ms == 250.0
