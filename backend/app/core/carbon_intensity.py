"""
Carbon Intensity Dataset and Calculator for GreenAgent OS
Provides multi-region baseline and 24-hour diurnal solar/wind curves with PUE calculations.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import math
from backend.app.core.data_contracts import CarbonEstimate, MeasurementMethod
from backend.app.config import settings


# Regional Base Grid Intensity (gCO2e / kWh) and 24h variation parameters
REGIONAL_CARBON_PROFILES: Dict[str, Dict[str, Any]] = {
    "us-east": {
        "region_name": "US East (N. Virginia)",
        "base_intensity_g_per_kwh": 375.0,
        "solar_factor": 60.0,    # Reduction during peak daylight hours
        "wind_factor": 30.0,
        "datacenter_pue": 1.25,
        "country": "USA"
    },
    "us-west": {
        "region_name": "US West (Oregon)",
        "base_intensity_g_per_kwh": 185.0, # High hydro/renewables
        "solar_factor": 50.0,
        "wind_factor": 40.0,
        "datacenter_pue": 1.18,
        "country": "USA"
    },
    "eu-central": {
        "region_name": "Europe Central (Frankfurt)",
        "base_intensity_g_per_kwh": 310.0,
        "solar_factor": 75.0,
        "wind_factor": 50.0,
        "datacenter_pue": 1.22,
        "country": "Germany"
    },
    "eu-north": {
        "region_name": "Europe North (Stockholm)",
        "base_intensity_g_per_kwh": 42.0,  # Nuclear + Hydro dominant
        "solar_factor": 10.0,
        "wind_factor": 15.0,
        "datacenter_pue": 1.15,
        "country": "Sweden"
    },
    "ap-south": {
        "region_name": "Asia Pacific (Mumbai)",
        "base_intensity_g_per_kwh": 610.0, # High coal baseline
        "solar_factor": 90.0,
        "wind_factor": 25.0,
        "datacenter_pue": 1.35,
        "country": "India"
    }
}


class CarbonCalculator:
    """
    Computes greenhouse gas emissions (CO2e) based on energy consumption,
    regional grid mix, datacenter PUE, and time-of-day diurnal dynamics.
    """

    @staticmethod
    def get_grid_intensity(region: str = "us-east", hour_of_day: Optional[int] = None) -> float:
        """
        Calculates the grid intensity (gCO2e/kWh) for a given region and hour (0-23 UTC).
        Models renewable generation peaks (solar peaks around midday 11:00-15:00 UTC local offset).
        """
        region_key = region.lower()
        profile = REGIONAL_CARBON_PROFILES.get(region_key, REGIONAL_CARBON_PROFILES["us-east"])
        base = profile["base_intensity_g_per_kwh"]

        if hour_of_day is None:
            hour_of_day = datetime.now(timezone.utc).hour

        # Solar curve: maximum solar abatement in local daytime hours (simulated sinusoidal wave)
        solar_phase = math.sin((hour_of_day - 6) / 24.0 * 2.0 * math.pi)
        solar_abatement = max(0.0, solar_phase) * profile["solar_factor"]

        # Night wind curve (stronger in late evening/early night)
        wind_phase = math.cos((hour_of_day - 2) / 24.0 * 2.0 * math.pi)
        wind_abatement = max(0.0, wind_phase) * (profile["wind_factor"] * 0.5)

        current_intensity = max(20.0, base - solar_abatement - wind_abatement)
        return round(current_intensity, 2)

    @classmethod
    def calculate_carbon(
        cls,
        workload_id: str,
        energy_joules: float,
        region: str = "us-east",
        override_intensity: Optional[float] = None,
        is_simulation: bool = False
    ) -> CarbonEstimate:
        """
        Computes CarbonEstimate from Joules.
        Formula:
          energy_kwh = energy_joules / 3,600,000
          carbon_grams = energy_kwh * datacenter_pue * grid_intensity (g/kWh)
        """
        profile = REGIONAL_CARBON_PROFILES.get(region.lower(), REGIONAL_CARBON_PROFILES["us-east"])
        pue = profile["datacenter_pue"]

        intensity = override_intensity if override_intensity is not None else cls.get_grid_intensity(region)
        energy_kwh = energy_joules / 3_600_000.0
        co2e_grams = energy_kwh * pue * intensity

        method = MeasurementMethod.SIMULATED_CARBON if is_simulation else MeasurementMethod.ESTIMATED_CARBON
        intensity_source = "externally_supplied" if override_intensity is not None else "simulated_regional_diurnal_grid_v1"

        return CarbonEstimate(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="1.0.0",
            source="greenagent-carbon-calculator",
            workload_id=workload_id,
            energy_joules=round(energy_joules, 4),
            energy_kwh=round(energy_kwh, 8),
            grid_region=region,
            grid_intensity_g_per_kwh=round(intensity, 2),
            pue=pue,
            estimated_co2e_grams=round(co2e_grams, 6),
            method=method,
            intensity_source=intensity_source,
            confidence=0.88 if override_intensity is None else 0.95
        )
