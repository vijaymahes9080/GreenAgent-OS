"""
Unit tests for GreenAgent OS Data Contracts
Validates field presence, versioning, timestamps, and provenance labeling.
"""
import pytest
from backend.app.core.data_contracts import (
    Workload, ModelProfile, ExecutionTrace, EnergyEstimate, CarbonEstimate,
    OptimizationDecision, SchedulingDecision, CacheEntry, QualityEvaluation,
    BenchmarkResult, MeasurementMethod, ComplexityLevel, SchedulingAction
)


def test_workload_contract():
    wl = Workload(name="Test Task", prompt="Analyze green energy trends.")
    assert wl.id is not None
    assert wl.timestamp is not None
    assert wl.version == "1.0.0"
    assert wl.source == "greenagent-core"
    assert wl.allow_cache is True


def test_energy_estimate_contract_transparency():
    ee = EnergyEstimate(
        workload_id="wl-100",
        model="llama3.2:1b",
        tokens_input=50,
        tokens_output=100,
        duration_seconds=0.45,
        joules=4.2,
        watt_hours=0.001166,
        method=MeasurementMethod.ESTIMATED_ENERGY,
        confidence=0.91
    )
    assert ee.method == MeasurementMethod.ESTIMATED_ENERGY
    assert ee.confidence == 0.91
    assert ee.joules == 4.2


def test_carbon_estimate_contract():
    ce = CarbonEstimate(
        workload_id="wl-100",
        energy_joules=3600.0,
        energy_kwh=0.001,
        grid_region="us-east",
        grid_intensity_g_per_kwh=375.0,
        pue=1.25,
        estimated_co2e_grams=0.46875,
        method=MeasurementMethod.ESTIMATED_CARBON,
        intensity_source="simulated_regional_diurnal_grid_v1"
    )
    assert ce.grid_region == "us-east"
    assert ce.method == MeasurementMethod.ESTIMATED_CARBON
    assert ce.estimated_co2e_grams > 0.4
