"""
CrewAI & AutoGen Agent Carbon Limiter Hook
Interprets multi-agent debate and reasoning loops, preventing runaway token consumption.
"""
from typing import Dict, Any, Optional


class MultiAgentCarbonGovernor:
    def __init__(self, max_carbon_budget_g: float = 0.50, max_energy_joules: float = 500.0):
        self.max_carbon_budget_g = max_carbon_budget_g
        self.max_energy_joules = max_energy_joules
        self.accumulated_joules = 0.0
        self.accumulated_carbon_g = 0.0
        self.total_rounds = 0

    def record_agent_step(self, agent_name: str, prompt_tokens: int, completion_tokens: int, model: str = "llama3.2:3b") -> Dict[str, Any]:
        """Tracks an individual agent-to-agent message step."""
        self.total_rounds += 1
        j_step = (prompt_tokens * 0.02) + (completion_tokens * 0.08)
        c_step = (j_step / 3600000.0) * 1.25 * 375.0

        self.accumulated_joules += j_step
        self.accumulated_carbon_g += c_step

        exceeded = (self.accumulated_carbon_g >= self.max_carbon_budget_g) or (self.accumulated_joules >= self.max_energy_joules)

        return {
            "round": self.total_rounds,
            "agent": agent_name,
            "step_joules": round(j_step, 3),
            "step_carbon_g": round(c_step, 5),
            "total_carbon_g": round(self.accumulated_carbon_g, 5),
            "budget_exceeded": exceeded,
            "action": "HALT_CONSENSUS" if exceeded else "CONTINUE"
        }
