"""
Energy Estimation Engine for GreenAgent OS
Strictly distinguishes measured hardware readings from parametric model estimates and simulated benchmarks.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from backend.app.core.data_contracts import EnergyEstimate, MeasurementMethod
from backend.app.config import settings


# Baseline model parameter power profiles (Joules per input / output token on CPU/standard host)
# Formula: E_active = (tokens_in * J_in + tokens_out * J_out) + (P_idle_w * duration_sec)
MODEL_ENERGY_PROFILES: Dict[str, Dict[str, float]] = {
    "llama3.2:1b": {
        "j_per_in_token": 0.008,
        "j_per_out_token": 0.035,
        "idle_power_watts": 15.0,
        "param_size_b": 1.2
    },
    "llama3.2:3b": {
        "j_per_in_token": 0.018,
        "j_per_out_token": 0.078,
        "idle_power_watts": 18.0,
        "param_size_b": 3.2
    },
    "mistral:7b": {
        "j_per_in_token": 0.042,
        "j_per_out_token": 0.185,
        "idle_power_watts": 28.0,
        "param_size_b": 7.2
    },
    "llama3.1:8b": {
        "j_per_in_token": 0.048,
        "j_per_out_token": 0.210,
        "idle_power_watts": 30.0,
        "param_size_b": 8.0
    },
    "qwen2.5:14b": {
        "j_per_in_token": 0.085,
        "j_per_out_token": 0.390,
        "idle_power_watts": 45.0,
        "param_size_b": 14.7
    },
    "mixtral:8x7b": {
        "j_per_in_token": 0.120,
        "j_per_out_token": 0.540,
        "idle_power_watts": 65.0,
        "param_size_b": 46.7
    },
    "deepseek-r1:8b": {
        "j_per_in_token": 0.052,
        "j_per_out_token": 0.235,
        "idle_power_watts": 32.0,
        "param_size_b": 8.1
    },
    "default": {
        "j_per_in_token": 0.040,
        "j_per_out_token": 0.180,
        "idle_power_watts": 25.0,
        "param_size_b": 7.0
    }
}


class EnergyEstimator:
    """
    Computes energy consumption for model execution.
    Maintains transparency across MEASURED, ESTIMATED, and SIMULATED modes.
    """

    @staticmethod
    def estimate_energy(
        workload_id: str,
        model: str,
        tokens_input: int,
        tokens_output: int,
        duration_seconds: float,
        measured_joules: Optional[float] = None,
        is_simulation: bool = False,
        hardware_target: str = "cpu_local"
    ) -> EnergyEstimate:
        """
        Calculates energy usage with strict labeling of methodology.
        """
        # 1. Measured Energy input from hardware counters (RAPL / NVML / PDU)
        if measured_joules is not None and measured_joules > 0.0:
            joules = float(measured_joules)
            method = MeasurementMethod.MEASURED_ENERGY
            confidence = 0.98
            details = {
                "source_instrument": "hardware_telemetry_counter",
                "hardware_target": hardware_target,
                "measured_joules": joules
            }
        else:
            # 2. Model-specific estimate or simulated estimate
            profile = MODEL_ENERGY_PROFILES.get(model.lower(), MODEL_ENERGY_PROFILES["default"])
            
            active_energy_in = tokens_input * profile["j_per_in_token"]
            active_energy_out = tokens_output * profile["j_per_out_token"]
            idle_energy = profile["idle_power_watts"] * max(0.01, duration_seconds)
            
            joules = active_energy_in + active_energy_out + idle_energy
            
            if is_simulation:
                method = MeasurementMethod.SIMULATED_CARBON # Simulation tag
                confidence = 0.82
                details = {
                    "estimation_model": "synthetic_benchmark_simulation",
                    "param_size_b": profile["param_size_b"]
                }
            else:
                method = MeasurementMethod.ESTIMATED_ENERGY
                confidence = 0.91
                details = {
                    "estimation_model": "active_plus_idle_parametric_v1",
                    "j_per_in_token": profile["j_per_in_token"],
                    "j_per_out_token": profile["j_per_out_token"],
                    "idle_power_watts": profile["idle_power_watts"],
                    "active_joules": round(active_energy_in + active_energy_out, 4),
                    "idle_joules": round(idle_energy, 4)
                }

        watt_hours = joules / 3600.0

        return EnergyEstimate(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="1.0.0",
            source="greenagent-energy-estimator",
            workload_id=workload_id,
            model=model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            duration_seconds=duration_seconds,
            joules=round(joules, 4),
            watt_hours=round(watt_hours, 6),
            method=method,
            hardware_target=hardware_target,
            confidence=confidence,
            details=details
        )
