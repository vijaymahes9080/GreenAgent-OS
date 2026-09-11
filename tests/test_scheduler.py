"""
Tests for Carbon-Aware Scheduler
Verifies invariant: never delay critical, emergency, or user-blocking tasks.
"""
from backend.app.core.data_contracts import (
    Workload, WorkloadPriority, SchedulingAction
)
from backend.app.services.scheduler_service import CarbonAwareScheduler


def test_scheduler_never_delays_emergency():
    wl = Workload(
        name="Urgent",
        prompt="Heart attack emergency triage",
        priority=WorkloadPriority.EMERGENCY,
        deadline_seconds=5.0,
        user_blocking=True,
        safety_sensitive=True
    )
    decision = CarbonAwareScheduler.schedule_workload(wl, estimated_energy_joules=10.0)
    assert decision.action in [SchedulingAction.EXECUTE_NOW, SchedulingAction.MOVE_REGION]
    assert decision.delay_seconds == 0.0


def test_scheduler_never_delays_user_blocking():
    wl = Workload(
        name="User Waiting",
        prompt="Format this sentence",
        deadline_seconds=60.0,
        user_blocking=True
    )
    decision = CarbonAwareScheduler.schedule_workload(wl, estimated_energy_joules=5.0)
    assert decision.delay_seconds == 0.0
    assert decision.action in [SchedulingAction.EXECUTE_NOW, SchedulingAction.MOVE_REGION]


def test_scheduler_flexible_delay():
    wl = Workload(
        name="Batch Reporting",
        prompt="Generate weekly statistics report",
        deadline_seconds=86400.0,  # 24h
        allow_delay=True,
        allow_region_shift=False
    )
    decision = CarbonAwareScheduler.schedule_workload(wl, estimated_energy_joules=25.0)
    # Either delay or execute now depending on current hour
    assert decision.action in [SchedulingAction.DELAY, SchedulingAction.EXECUTE_NOW]
