"""
Core Data Contracts for GreenAgent OS
All schemas enforce strict provenance, timestamping, versioning, and estimation method transparency.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


def current_iso_time() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    u = str(uuid.uuid4())[:8]
    return f"{prefix}_{u}" if prefix else str(uuid.uuid4())


class MeasurementMethod(str, Enum):
    MEASURED_ENERGY = "measured_energy"           # Hardware counters (RAPL, NVML, Powermetrics)
    ESTIMATED_ENERGY = "estimated_energy"         # Model profiling formula (Joules = t_in*e_in + t_out*e_out)
    ESTIMATED_CARBON = "estimated_carbon"         # Energy * Grid Intensity * PUE
    SIMULATED_CARBON = "simulated_carbon"         # Synthesized/Simulated grid trace
    EXTERNALLY_SUPPLIED = "externally_supplied"   # Third-party grid API (WattTime, ElectricityMaps)


class ComplexityLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    CRITICAL = "CRITICAL"


class SchedulingAction(str, Enum):
    EXECUTE_NOW = "EXECUTE_NOW"
    DELAY = "DELAY"
    MOVE_REGION = "MOVE_REGION"
    USE_SMALLER_MODEL = "USE_SMALLER_MODEL"
    USE_CACHE = "USE_CACHE"


class WorkloadPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    CACHED = "CACHED"


# -----------------------------------------------------------------------------
# Base Contract
# -----------------------------------------------------------------------------
class BaseContract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=current_iso_time)
    version: str = Field(default="1.0.0")
    source: str = Field(default="greenagent-core")


# -----------------------------------------------------------------------------
# 1. Workload
# -----------------------------------------------------------------------------
class Workload(BaseContract):
    name: str
    prompt: str
    system_prompt: Optional[str] = None
    expected_output_format: Optional[str] = "text"
    priority: WorkloadPriority = WorkloadPriority.NORMAL
    deadline_seconds: float = Field(default=60.0, description="Max acceptable latency/delay in seconds")
    user_blocking: bool = Field(default=False, description="True if a human user is interactively waiting")
    safety_sensitive: bool = Field(default=False, description="True if safety/medical/legal/critical")
    allow_cache: bool = Field(default=True)
    allow_delay: bool = Field(default=True)
    allow_region_shift: bool = Field(default=True)
    preferred_region: str = "us-east"
    required_quality_min: float = Field(default=0.85, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# 2. Model Profile
# -----------------------------------------------------------------------------
class ModelProfile(BaseContract):
    name: str                                # e.g. "llama3.2:1b"
    provider: str                            # e.g. "ollama", "mock", "vllm"
    capability_score: float = Field(ge=0.0, le=1.0) # 0.0 to 1.0 (benchmarked reasoning strength)
    latency_estimate_ms: float               # typical generation latency baseline (ms)
    energy_estimate_j_per_token: float       # Joules per generated token estimate
    cost_estimate_per_1k_tokens: float       # Financial cost in USD per 1k tokens
    context_window: int                      # Context tokens limit
    availability: bool = True
    quality_benchmark: Dict[str, float] = Field(default_factory=dict) # e.g. {"gsm8k": 0.65, "humaneval": 0.58}
    supported_complexity: List[ComplexityLevel] = Field(
        default_factory=lambda: [ComplexityLevel.EASY, ComplexityLevel.MEDIUM]
    )


# -----------------------------------------------------------------------------
# 3. Energy Estimate
# -----------------------------------------------------------------------------
class EnergyEstimate(BaseContract):
    workload_id: str
    model: str
    tokens_input: int
    tokens_output: int
    duration_seconds: float
    joules: float
    watt_hours: float
    method: MeasurementMethod
    hardware_target: str = "cpu_generic"    # e.g. "apple_m_series", "intel_xeon", "nvidia_t4_sim"
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    details: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# 4. Carbon Estimate
# -----------------------------------------------------------------------------
class CarbonEstimate(BaseContract):
    workload_id: str
    energy_joules: float
    energy_kwh: float
    grid_region: str
    grid_intensity_g_per_kwh: float          # gCO2e / kWh
    pue: float = 1.25                        # Datacenter Power Usage Effectiveness
    estimated_co2e_grams: float              # Grams CO2e emitted
    method: MeasurementMethod
    intensity_source: str                    # e.g. "simulated_hourly_trace", "external_api"
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)


# -----------------------------------------------------------------------------
# 5. Scheduling Decision
# -----------------------------------------------------------------------------
class SchedulingDecision(BaseContract):
    workload_id: str
    action: SchedulingAction
    scheduled_region: str
    scheduled_time: str
    delay_seconds: float = 0.0
    rationale: str
    carbon_reduction_predicted_pct: float = 0.0
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)


# -----------------------------------------------------------------------------
# 6. Optimization Decision
# -----------------------------------------------------------------------------
class OptimizationDecision(BaseContract):
    workload_id: str
    detected_complexity: ComplexityLevel
    selected_model: str
    scheduling_action: SchedulingAction
    target_region: str
    use_cache: bool
    predicted_latency_ms: float
    predicted_energy_joules: float
    predicted_carbon_grams: float
    predicted_cost_usd: float
    predicted_quality_score: float
    weights_applied: Dict[str, float]        # alpha, beta, gamma, delta, epsilon
    optimization_objective_value: float
    rationale: List[str]
    confidence: float = Field(default=0.88, ge=0.0, le=1.0)


# -----------------------------------------------------------------------------
# 7. Execution Trace (Telemetry)
# -----------------------------------------------------------------------------
class ExecutionTrace(BaseContract):
    workload_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    retries: int = 0
    tool_calls_count: int = 0
    tool_calls_latency_ms: float = 0.0
    cache_hit: bool = False
    status: ExecutionStatus = ExecutionStatus.COMPLETED
    raw_response: Optional[str] = None
    energy_estimate: Optional[EnergyEstimate] = None
    carbon_estimate: Optional[CarbonEstimate] = None
    error_message: Optional[str] = None


# -----------------------------------------------------------------------------
# 8. Cache Entry
# -----------------------------------------------------------------------------
class CacheEntry(BaseContract):
    key_hash: str
    prompt: str
    response: str
    model: str
    tokens_saved: int
    energy_saved_joules: float
    carbon_saved_grams: float
    ttl_seconds: int
    expires_at: str
    hit_count: int = 0
    safety_tier: str = "general"
    embedding: Optional[List[float]] = None
    provenance_metadata: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# 9. Quality Evaluation
# -----------------------------------------------------------------------------
class QualityEvaluation(BaseContract):
    workload_id: str
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    factual_consistency: float = Field(ge=0.0, le=1.0)
    task_completion: float = Field(ge=0.0, le=1.0)
    required_fields_present: bool
    tool_call_success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    meets_threshold: bool
    rejection_occurred: bool = False
    rejection_reason: Optional[str] = None
    suggested_fallback_model: Optional[str] = None
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)


# -----------------------------------------------------------------------------
# 10. Benchmark Result
# -----------------------------------------------------------------------------
class BenchmarkResult(BaseContract):
    benchmark_name: str
    total_workloads: int
    baseline_metrics: Dict[str, float]
    optimized_metrics: Dict[str, float]
    percentage_changes: Dict[str, float]
    targets_achieved: Dict[str, bool]
    verdict: str
    details: List[Dict[str, Any]] = Field(default_factory=list)
