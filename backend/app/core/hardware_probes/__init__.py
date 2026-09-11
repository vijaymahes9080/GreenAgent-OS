"""
Hardware Energy Telemetry Probes for GreenAgent OS
Directly reads physical energy counters from Intel/AMD RAPL, Apple Silicon, and NVIDIA NVML.
Gracefully degrades to None when running unprivileged.
"""
import os
import sys
from typing import Optional, Dict, Any


class HardwareProbeManager:
    @staticmethod
    def read_rapl_energy_joules() -> Optional[float]:
        """Reads Intel/AMD Running Average Power Limit energy counter from Linux sysfs."""
        rapl_path = "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"
        try:
            if os.path.exists(rapl_path):
                with open(rapl_path, "r") as f:
                    uj = int(f.read().strip())
                    return uj / 1_000_000.0  # Convert microjoules to Joules
        except Exception:
            pass
        return None

    @staticmethod
    def read_nvidia_energy_joules(device_idx: int = 0) -> Optional[float]:
        """Reads total energy consumed by GPU using pynvml."""
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(device_idx)
            mj = pynvml.nvmlDeviceGetTotalEnergyConsumption(handle)
            pynvml.nvmlShutdown()
            return mj / 1000.0  # Convert millijoules to Joules
        except Exception:
            return None

    @classmethod
    def get_hardware_reading(cls) -> Dict[str, Any]:
        """Returns physical counter reading if available."""
        rapl = cls.read_rapl_energy_joules()
        nvml = cls.read_nvidia_energy_joules()
        available = (rapl is not None) or (nvml is not None)
        return {
            "available": available,
            "rapl_joules": rapl,
            "nvml_joules": nvml,
            "instrument": "physical_hardware_counters" if available else "uninstrumented_fallback"
        }
