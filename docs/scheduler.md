# Carbon-Aware Scheduler Specification

## Overview

The GreenAgent OS Scheduler coordinates the temporal and geographical execution of AI workloads to minimize carbon intensity without compromising deadlines or safety.

## Scheduling Actions

| Action | Description | Conditions |
| :--- | :--- | :--- |
| `EXECUTE_NOW` | Dispatches task immediately on local/preferred cluster. | Emergency, critical, user-blocking, or latency &le; 10s. |
| `MOVE_REGION` | Dispatches task immediately to a lower-carbon region. | Cleaner grid available (e.g. EU-North hydro/nuclear). |
| `DELAY` | Enqueues task for delayed dispatch during renewable valley. | Background/batch tasks with deadline &ge; 30 mins. |
| `USE_SMALLER_MODEL` | Replaces heavy model with energy-efficient tier. | Low complexity task meeting minimum capability. |
| `USE_CACHE` | Resolves output from semantic cache without inference. | Non-volatile, cacheable prompt with similarity &ge; 0.90. |

---

## The Safety Invariant

```
INVARIANT:
IF (Priority ∈ {CRITICAL, EMERGENCY} OR User_Blocking == True OR Deadline <= 10s)
THEN
    Action ∈ {EXECUTE_NOW, MOVE_REGION}
    Delay_Seconds == 0.0
```

Under NO circumstances will the scheduler delay a safety-critical, medical, legal, or interactive user-blocking task to save energy or carbon.
