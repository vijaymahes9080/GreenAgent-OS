"""
Departmental Carbon Budgeting & Quota Controller
Tracks monthly kgCO2e carbon allowances per team or API tenant.
"""
from typing import Dict, Any


class TeamCarbonBudgetController:
    # Team quotas in kg CO2e per month
    _BUDGETS: Dict[str, Dict[str, float]] = {
        "engineering": {"limit_kg": 10.0, "used_kg": 1.42},
        "customer_support": {"limit_kg": 5.0, "used_kg": 4.10},
        "analytics": {"limit_kg": 8.0, "used_kg": 0.85},
    }

    @classmethod
    def check_and_deduct(cls, team_id: str, emissions_grams: float) -> Dict[str, Any]:
        """Validates if team budget allows execution and updates consumption."""
        budget = cls._BUDGETS.get(team_id, {"limit_kg": 5.0, "used_kg": 0.0})
        emissions_kg = emissions_grams / 1000.0

        if budget["used_kg"] + emissions_kg > budget["limit_kg"]:
            return {
                "allowed": False,
                "team_id": team_id,
                "used_kg": budget["used_kg"],
                "limit_kg": budget["limit_kg"],
                "message": f"Carbon budget exceeded for team '{team_id}'. Request throttled."
            }

        budget["used_kg"] += emissions_kg
        cls._BUDGETS[team_id] = budget

        return {
            "allowed": True,
            "team_id": team_id,
            "used_kg": round(budget["used_kg"], 4),
            "remaining_kg": round(budget["limit_kg"] - budget["used_kg"], 4),
            "utilization_pct": round((budget["used_kg"] / budget["limit_kg"]) * 100, 1)
        }
