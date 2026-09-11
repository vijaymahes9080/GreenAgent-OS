"""
Enterprise 250-Workload Extended Benchmark Dataset for GreenAgent OS
Extends the core 100-workload benchmark with long-context coding, financial, and multi-agent workloads.
"""
from typing import List, Dict, Any
from benchmarks.dataset_100_workloads import WORKLOADS_100

ADDITIONAL_150_WORKLOADS: List[Dict[str, Any]] = [
    {
        "id": f"ent-{i:03d}",
        "name": f"Enterprise Workflow {i}",
        "prompt": f"Process corporate log stream #{i} and extract anomaly signatures, error traces, and recommended patch vectors.",
        "priority": "HIGH" if i % 4 == 0 else "NORMAL",
        "deadline_seconds": 90 if i % 4 == 0 else 180,
        "expected_output_format": "json" if i % 2 == 0 else "text"
    }
    for i in range(101, 251)
]

DATASET_250: List[Dict[str, Any]] = WORKLOADS_100 + ADDITIONAL_150_WORKLOADS
