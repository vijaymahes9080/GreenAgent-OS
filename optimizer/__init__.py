"""
Standalone Optimizer Module for GreenAgent OS
Can be imported by external agent frameworks (LangGraph, AutoGen, CrewAI).
"""
from backend.app.services.multi_objective_optimizer import MultiObjectiveOptimizer

__all__ = ["MultiObjectiveOptimizer"]
