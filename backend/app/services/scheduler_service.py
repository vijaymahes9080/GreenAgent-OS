"""
Carbon-Aware Scheduler for GreenAgent OS
Schedules AI workloads to minimize carbon emissions via temporal delay or regional shifting,
while strictly enforcing user deadlines and safety invariant: never delay critical or blocking tasks.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import uuid

from backend.app.core.data_contracts import (
    Workload, SchedulingAction, SchedulingDecision, WorkloadPriority, ComplexityLevel
)
from backend.app.core.carbon_intensity import CarbonCalculator, REGIONAL_CARBON_PROFILES


class CarbonAwareScheduler:
    """Carbon-aware temporal and spatial task scheduler."""

    @classmethod
    def schedule_workload(
        cls,
        workload: Workload,
        estimated_energy_joules: float,
        current_region: str = "us-east"
    ) -> SchedulingDecision:
        """
        Determines the optimal scheduling action:
        - EXECUTE_NOW: If critical, user-blocking, or tight deadline (< 10s).
        - MOVE_REGION: If a cleaner geographical region is available with lower carbon intensity.
        - DELAY: If a significant carbon valley occurs within the allowable deadline window.
        """
        current_hour = datetime.now(timezone.utc).hour
        local_intensity = CarbonCalculator.get_grid_intensity(current_region, current_hour)

        # INVARIANT: Never delay emergency, critical, or user-blocking workloads
        if (
            workload.user_blocking or
            workload.safety_sensitive or
            workload.priority in [WorkloadPriority.CRITICAL, WorkloadPriority.EMERGENCY] or
            workload.deadline_seconds <= 10.0
        ):
            # Still check if we can seamlessly shift region without delaying
            if workload.allow_region_shift:
                best_region, best_intensity = cls._find_cleanest_region(current_hour)
                if best_intensity < local_intensity * 0.70:
                    carbon_saving_pct = ((local_intensity - best_intensity) / local_intensity) * 100.0
                    return SchedulingDecision(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        version="1.0.0",
                        source="greenagent-carbon-scheduler",
                        workload_id=workload.id,
                        action=SchedulingAction.MOVE_REGION,
                        scheduled_region=best_region,
                        scheduled_time=datetime.now(timezone.utc).isoformat(),
                        delay_seconds=0.0,
                        rationale=f"Immediate execution required for blocking/critical workload, shifted from {current_region} ({local_intensity}g) to cleanest region {best_region} ({best_intensity}g)",
                        carbon_reduction_predicted_pct=round(carbon_saving_pct, 1),
                        confidence=0.95
                    )

            return SchedulingDecision(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                version="1.0.0",
                source="greenagent-carbon-scheduler",
                workload_id=workload.id,
                action=SchedulingAction.EXECUTE_NOW,
                scheduled_region=current_region,
                scheduled_time=datetime.now(timezone.utc).isoformat(),
                delay_seconds=0.0,
                rationale="Immediate execution mandated by critical priority, user-blocking latency, or tight deadline",
                carbon_reduction_predicted_pct=0.0,
                confidence=0.99
            )

        # 2. Check for Temporal Delay within deadline (e.g. background batch processing)
        if workload.allow_delay and workload.deadline_seconds >= 1800.0:  # >= 30 minutes
            max_delay_hours = int(min(12, workload.deadline_seconds // 3600))
            best_hour = current_hour
            min_future_intensity = local_intensity

            for offset in range(1, max_delay_hours + 1):
                future_hour = (current_hour + offset) % 24
                intensity = CarbonCalculator.get_grid_intensity(current_region, future_hour)
                if intensity < min_future_intensity:
                    min_future_intensity = intensity
                    best_hour = future_hour

            # If postponing yields >= 20% carbon reduction, schedule delay
            if min_future_intensity < local_intensity * 0.80:
                hours_to_wait = (best_hour - current_hour) % 24
                delay_sec = float(hours_to_wait * 3600)
                sched_time = datetime.now(timezone.utc) + timedelta(seconds=delay_sec)
                saving_pct = ((local_intensity - min_future_intensity) / local_intensity) * 100.0

                return SchedulingDecision(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    version="1.0.0",
                    source="greenagent-carbon-scheduler",
                    workload_id=workload.id,
                    action=SchedulingAction.DELAY,
                    scheduled_region=current_region,
                    scheduled_time=sched_time.isoformat(),
                    delay_seconds=delay_sec,
                    rationale=f"Delayed by {hours_to_wait}h to synchronize with renewable generation peak ({min_future_intensity} gCO2e/kWh vs {local_intensity} gCO2e/kWh)",
                    carbon_reduction_predicted_pct=round(saving_pct, 1),
                    confidence=0.90
                )

        # 3. Check for Regional Shift (spatial arbitrage)
        if workload.allow_region_shift:
            best_region, best_intensity = cls._find_cleanest_region(current_hour)
            if best_intensity < local_intensity * 0.75:
                saving_pct = ((local_intensity - best_intensity) / local_intensity) * 100.0
                return SchedulingDecision(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    version="1.0.0",
                    source="greenagent-carbon-scheduler",
                    workload_id=workload.id,
                    action=SchedulingAction.MOVE_REGION,
                    scheduled_region=best_region,
                    scheduled_time=datetime.now(timezone.utc).isoformat(),
                    delay_seconds=0.0,
                    rationale=f"Routed from high-carbon grid {current_region} ({local_intensity}g) to low-carbon grid {best_region} ({best_intensity}g)",
                    carbon_reduction_predicted_pct=round(saving_pct, 1),
                    confidence=0.93
                )

        # Default to execute now
        return SchedulingDecision(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="1.0.0",
            source="greenagent-carbon-scheduler",
            workload_id=workload.id,
            action=SchedulingAction.EXECUTE_NOW,
            scheduled_region=current_region,
            scheduled_time=datetime.now(timezone.utc).isoformat(),
            delay_seconds=0.0,
            rationale="Current region and time window are optimal under given workload constraints",
            carbon_reduction_predicted_pct=0.0,
            confidence=0.92
        )

    @classmethod
    def _find_cleanest_region(cls, hour_of_day: int) -> Tuple[str, float]:
        """Finds region with lowest current carbon intensity."""
        best_region = "us-east"
        lowest_intensity = 9999.0
        for region in REGIONAL_CARBON_PROFILES.keys():
            intensity = CarbonCalculator.get_grid_intensity(region, hour_of_day)
            if intensity < lowest_intensity:
                lowest_intensity = intensity
                best_region = region
        return best_region, lowest_intensity
