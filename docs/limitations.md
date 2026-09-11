# Limitations & Honest Engineering Constraints

GreenAgent OS is built on rigorous transparency. We document the current engineering boundaries of the platform:

---

## 1. Hardware Energy Counter Access
- **Constraint**: Accessing physical RAPL counters (`/dev/cpu/*/msr`) or NVIDIA NVML registers requires root or privileged container capabilities (`CAP_SYS_RAWIO`).
- **Mitigation**: When physical counter access is unavailable, GreenAgent OS gracefully falls back to parameter-calibrated equations and explicitly tags output as `ESTIMATED_ENERGY` rather than misrepresenting it as hardware-measured.

---

## 2. Grid Carbon Intensity Granularity
- **Constraint**: National and regional grid balancing authorities report marginal carbon intensity at 5 to 60-minute intervals. Local distribution transmission congestion or behind-the-meter solar curtailment cannot always be captured in real time.
- **Mitigation**: Outputs carry `confidence` scores and explicit source attribution tags (`simulated_regional_diurnal_grid_v1`, `externally_supplied`).

---

## 3. Cache Hit Rate Dependency
- **Constraint**: High model-call reduction (80%+) depends on workloads exhibiting natural redundancy (repeated user questions, common customer support issues, recurring automated steps). Unique one-off queries achieve savings primarily through model tiering and spatial grid shifting.

---

## 4. Latency vs Carbon Trade-off
- **Constraint**: Temporal delaying (`DELAY`) is only suitable for non-interactive workloads (batch indexing, document extraction, periodic digests). Interactive user queries must rely on spatial routing (`MOVE_REGION`) or small-model distillation (`USE_SMALLER_MODEL`).
