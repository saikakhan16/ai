"""
FD Portfolio Optimizer — SIMPLIFIED 3-Agent CrewAI System
LLM: Groq (Llama 3.3 70B) — Free & Efficient
Compatible with CrewAI 1.x
"""

import os
import json
from crewai import Crew, Process
from config.llm import get_llm
from agents.data_collector import build_data_collector
from agents.pso_optimizer import build_pso_optimizer
from agents.user_advisor import build_user_advisor
from tasks import collect_rates_task, optimize_portfolio_task, user_advisory_task


def run_fd_crew(user_input: dict) -> dict:
    llm = get_llm()

    # Only 3 essential agents instead of 6
    data_collector = build_data_collector(llm)
    pso_optimizer  = build_pso_optimizer(llm)
    user_advisor   = build_user_advisor(llm)

    # Simplified task chain: rates → optimization → report
    t1_rates    = collect_rates_task(data_collector, user_input)
    t2_optimize = optimize_portfolio_task(pso_optimizer, user_input, context=[t1_rates])
    t3_advise   = user_advisory_task(user_advisor, user_input, context=[t2_optimize])

    fd_crew = Crew(
        agents=[data_collector, pso_optimizer, user_advisor],
        tasks=[t1_rates, t2_optimize, t3_advise],
        process=Process.sequential,
        verbose=False,  # Disable verbose to reduce overhead
    )

    result = fd_crew.kickoff(inputs=user_input)
    return {"report": str(result)}


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   FD PORTFOLIO OPTIMIZER — CREW AI SYSTEM")
    print("   3 Agents · Groq LLM · PSO Algorithm")
    print("=" * 60 + "\n")

    user_request = {
        "amount": 1000000,
        "risk_profile": "moderate",
        "tenure_months": 12,
        "name": "Demo User"
    }

    print(f"User Request:\n{json.dumps(user_request, indent=2)}\n")
    result = run_fd_crew(user_request)

    print("\n" + "=" * 60)
    print("FINAL PORTFOLIO REPORT")
    print("=" * 60)
    print(result["report"])
