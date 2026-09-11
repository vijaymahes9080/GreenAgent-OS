"""
Datacenter Battery Energy Storage System (BESS) Co-Optimizer
Coordinates onsite battery discharge during peak utility carbon hours to power AI clusters.
"""
from typing import Dict, Any


class BESSCoOptimizer:
    def __init__(self, battery_capacity_kwh: float = 100.0, current_soc_pct: float = 85.0):
        self.battery_capacity_kwh = battery_capacity_kwh
        self.current_soc_pct = current_soc_pct  # State of Charge

    def evaluate_power_source(self, grid_intensity_g_kwh: float, required_energy_kwh: float) -> Dict[str, Any]:
        """
        If grid carbon intensity > 300 g/kWh and battery has > 20% SoC,
        discharge battery to absorb inference carbon footprint.
        """
        can_discharge = self.current_soc_pct > 20.0 and self.battery_capacity_kwh * (self.current_soc_pct / 100.0) >= required_energy_kwh

        if grid_intensity_g_kwh >= 300.0 and can_discharge:
            # Discharge battery
            kwh_used = required_energy_kwh
            pct_used = (kwh_used / self.battery_capacity_kwh) * 100.0
            self.current_soc_pct -= pct_used
            avoided_carbon_g = kwh_used * grid_intensity_g_kwh * 1.25

            return {
                "power_source": "ONSITE_CLEAN_BATTERY_BESS",
                "effective_grid_intensity_g_kwh": 0.0,
                "avoided_carbon_g": round(avoided_carbon_g, 4),
                "remaining_soc_pct": round(self.current_soc_pct, 1),
                "action": "DISCHARGE_BATTERY"
            }

        return {
            "power_source": "UTILITY_GRID",
            "effective_grid_intensity_g_kwh": grid_intensity_g_kwh,
            "avoided_carbon_g": 0.0,
            "remaining_soc_pct": round(self.current_soc_pct, 1),
            "action": "UTILITY_PASS_THROUGH"
        }
