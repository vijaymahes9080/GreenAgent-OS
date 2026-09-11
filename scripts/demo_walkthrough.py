#!/usr/bin/env python3
"""
GreenAgent OS Live Interactive Terminal Demonstration
Showcases prompt compression, semantic caching, and carbon-aware spatial routing in real-time.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.data_contracts import Workload
from backend.app.services.multi_objective_optimizer import MultiObjectiveOptimizer
from optimizer.prompt_compressor import PromptTokenCompressor


def run_demo():
    print("=" * 70)
    print("  GREENAGENT OS — LIVE OPTIMIZATION & CARBON SAVINGS DEMO")
    print("=" * 70)

    raw_prompt = (
        "Basically in order to analyze the data, it goes without saying that we need to furthermore "
        "summarize the quarterly datacenter power usage effectiveness metrics and identify renewable solar peaks."
    )
    print(f"\n[Step 1] Ingesting Raw User Prompt:\n\"{raw_prompt}\"")

    # 1. Prompt Compression
    compressed, stats = PromptTokenCompressor.compress_prompt(raw_prompt)
    print(f"\n[Step 2] Pre-Inference Token Compression:")
    print(f"Compressed Text: \"{compressed}\"")
    print(f"Token Reduction: -{stats['reduction_pct']}% (Eliminated {stats['tokens_saved']} redundant tokens)")

    # 2. Multi-Objective Optimization
    print(f"\n[Step 3] Running Multi-Objective Optimization Solver...")
    time.sleep(0.4)
    wl = Workload(name="LiveDemoTask", prompt=compressed, preferred_region="us-east")
    decision = MultiObjectiveOptimizer.optimize(wl)

    print(f"Detected Complexity:  {decision.detected_complexity.value}")
    print(f"Selected Model:       {decision.selected_model}")
    print(f"Scheduling Action:    {decision.scheduling_action.value}")
    print(f"Target Region:        {decision.target_region}")
    print(f"Predicted Carbon:     {decision.predicted_carbon_grams:.6f} g CO2e")
    print(f"Predicted Latency:    {decision.predicted_latency_ms:.1f} ms")

    print("\n[Step 4] Decision Explainability Rationale:")
    for r in decision.rationale:
        print(f"  • {r}")

    print("\n" + "=" * 70)
    print("  DEMO COMPLETE: Zero GPU required, 100% deterministic & transparent.")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
