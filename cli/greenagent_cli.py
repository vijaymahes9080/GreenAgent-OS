#!/usr/bin/env python3
"""
GreenAgent OS Command-Line Interface (CLI)
Provides command-line profiling, benchmark runs, and cache controls.
"""
import argparse
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.energy_estimator import EnergyEstimator
from backend.app.core.carbon_intensity import CarbonCalculator
from benchmarks.run_benchmark import run_benchmark


def main():
    parser = argparse.ArgumentParser(description="GreenAgent OS CLI — Carbon & Energy Optimizer")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: profile
    prof_p = subparsers.add_parser("profile", help="Profiles prompt token energy and carbon impact")
    prof_p.add_argument("prompt", type=str, help="Prompt text to profile")
    prof_p.add_argument("--model", type=str, default="llama3.2:3b")
    prof_p.add_argument("--region", type=str, default="us-east")

    # Command: bench
    subparsers.add_parser("bench", help="Runs the 100-workload sustainability benchmark")

    # Command: grid
    grid_p = subparsers.add_parser("grid", help="Checks current regional grid carbon intensities")
    grid_p.add_argument("--region", type=str, default="us-east")

    args = parser.parse_args()

    if args.command == "profile":
        tokens = len(args.prompt.split()) * 2
        ee = EnergyEstimator.estimate_energy("cli-job", args.model, tokens, 80, 0.40)
        ce = CarbonCalculator.calculate_carbon("cli-job", ee.joules, args.region)
        print(f"\n[GreenAgent Profile Result]")
        print(f"Model:           {args.model}")
        print(f"Tokens:          {tokens + 80}")
        print(f"Estimated Energy: {ee.joules:.3f} Joules ({ee.watt_hours:.6f} Wh)")
        print(f"Estimated Carbon: {ce.estimated_co2e_grams:.5f} g CO2e ({args.region})")

    elif args.command == "bench":
        run_benchmark()

    elif args.command == "grid":
        intensity = CarbonCalculator.get_grid_intensity(args.region)
        print(f"\n[Regional Grid Carbon Intensity]")
        print(f"Region:    {args.region}")
        print(f"Intensity: {intensity} gCO2e/kWh")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
