"""
Fine-Tuning vs RAG Carbon Trade-off Break-even Calculator
Models lifecycle greenhouse gas emissions comparing heavy-context RAG vs fine-tuned small model inference.
"""
from typing import Dict, Any


class RagVsFineTuneAnalyzer:
    @staticmethod
    def calculate_breakeven_queries(
        rag_context_tokens: int = 2000,
        rag_model_j_per_token: float = 0.540,      # e.g. 70B parameter model
        finetuned_model_j_per_token: float = 0.078, # e.g. 3B parameter model
        finetune_training_energy_kwh: float = 12.0  # Training run electricity
    ) -> Dict[str, Any]:
        """
        Calculates the query threshold where upfront training energy is amortized
        by smaller per-query inference costs.
        """
        training_joules = finetune_training_energy_kwh * 3_600_000.0

        # Energy per RAG query vs fine-tuned query (assuming 150 completion tokens)
        rag_query_joules = (rag_context_tokens + 150) * rag_model_j_per_token
        ft_query_joules = (150 + 150) * finetuned_model_j_per_token
        delta_joules_per_query = max(0.1, rag_query_joules - ft_query_joules)

        breakeven_queries = int(training_joules / delta_joules_per_query)

        return {
            "training_energy_kwh": finetune_training_energy_kwh,
            "rag_query_joules": round(rag_query_joules, 2),
            "finetuned_query_joules": round(ft_query_joules, 2),
            "joules_saved_per_query": round(delta_joules_per_query, 2),
            "breakeven_query_count": breakeven_queries,
            "recommendation": (
                f"Fine-tuning becomes environmentally net-positive after {breakeven_queries:,} queries."
            )
        }
