"""
Unit tests for Advanced GreenAgent OS Innovations:
- Prompt Token Compressor
- BESS Battery Co-Optimizer
- Speculative Early-Exit Layer Skipping
- Departmental Carbon Budget Controller
- Hardware Probes
"""
from optimizer.prompt_compressor import PromptTokenCompressor
from optimizer.speculative_early_exit import SpeculativeEarlyExitOptimizer
from scheduler.bess_co_optimizer import BESSCoOptimizer
from backend.app.services.budget_service import TeamCarbonBudgetController
from backend.app.core.hardware_probes import HardwareProbeManager


def test_prompt_token_compressor():
    prompt = "Basically in order to accomplish the task, it goes without saying that we must analyze data."
    compressed, stats = PromptTokenCompressor.compress_prompt(prompt)
    assert stats["compressed"] is True
    assert stats["tokens_saved"] > 0
    assert "Basically" not in compressed


def test_speculative_early_exit_simulation():
    res = SpeculativeEarlyExitOptimizer.evaluate_early_exit(total_layers=32)
    assert res["flop_reduction_pct"] > 10.0
    assert res["energy_saved_joules"] > 0.0


def test_bess_co_optimizer_battery_dispatch():
    bess = BESSCoOptimizer(battery_capacity_kwh=50.0, current_soc_pct=90.0)
    # Dirty grid (400 g/kWh) triggers battery discharge
    res = bess.evaluate_power_source(grid_intensity_g_kwh=400.0, required_energy_kwh=0.5)
    assert res["power_source"] == "ONSITE_CLEAN_BATTERY_BESS"
    assert res["action"] == "DISCHARGE_BATTERY"
    assert res["avoided_carbon_g"] > 0.0


def test_team_carbon_budget_controller():
    res = TeamCarbonBudgetController.check_and_deduct("analytics", emissions_grams=50.0)
    assert res["allowed"] is True
    assert res["used_kg"] > 0.0


def test_hardware_probe_manager_structure():
    res = HardwareProbeManager.get_hardware_reading()
    assert "available" in res
    assert "instrument" in res
