"""
FD Portfolio Optimizer — 6-Agent CrewAI System
LLM: Groq (Llama 3.3 70B) — Free & Fast (500 tokens/sec)

Agent Pipeline:
  User Request
      ↓
  [Agent 1] Orchestrator       — breaks down task, assigns agents
      ↓
  [Agent 2] Data Collector     — fetches live FD rates
  [Agent 3] Market Intelligence — RBI/macro analysis
      ↓ (parallel)
  [Agent 4] PSO Optimizer      — runs swarm algorithm
      ↓
  [Agent 5] Tax & Compliance   — TDS, DICGC, Form 15G
      ↓
  [Agent 6] User Advisor       — plain-language final report
"""

import os
from crewai import Crew, Process
from crewai.project import CrewBase, agent, crew, task
from agents.orchestrator import build_orchestrator
from agents.data_collector import build_data_collector
from agents.market_intel import build_market_intel
from agents.pso_optimizer import build_pso_optimizer
from agents.tax_compliance import build_tax_compliance
from agents.user_advisor import build_user_advisor
from tasks import (
    collect_rates_task,
    analyze_market_task,
    optimize_portfolio_task,
    tax_compliance_task,
    user_advisory_task,
    orchestrate_task
)
from config.llm import get_llm
import json


def run_fd_crew(user_input: dict) -> dict:
    """
    Main entry point. Pass user portfolio request, get optimized result.
    
    Args:
        user_input: {
            "amount": 1000000,
            "risk_profile": "moderate",  # conservative | moderate | aggressive
            "tenure_months": 12,
            "name": "Rahul"              # optional
        }
    
    Returns:
        Full portfolio report from all 6 agents
    """
    llm = get_llm()

    # ── Build all 6 agents ──────────────────────────────────────────────────
    orchestrator    = build_orchestrator(llm)
    data_collector  = build_data_collector(llm)
    market_intel    = build_market_intel(llm)
    pso_optimizer   = build_pso_optimizer(llm)
    tax_compliance  = build_tax_compliance(llm)
    user_advisor    = build_user_advisor(llm)

    # ── Build tasks with context chaining ──────────────────────────────────
    t1_rates   = collect_rates_task(data_collector, user_input)
    t2_market  = analyze_market_task(market_intel, user_input)
    t3_optimize= optimize_portfolio_task(pso_optimizer, user_input, context=[t1_rates, t2_market])
    t4_tax     = tax_compliance_task(tax_compliance, user_input, context=[t3_optimize])
    t5_advise  = user_advisory_task(user_advisor, user_input, context=[t3_optimize, t4_tax, t2_market])

    # ── Assemble the Crew ──────────────────────────────────────────────────
    fd_crew = Crew(
        agents=[orchestrator, data_collector, market_intel, pso_optimizer, tax_compliance, user_advisor],
        tasks=[t1_rates, t2_market, t3_optimize, t4_tax, t5_advise],
        process=Process.sequential,
        verbose=True,
        memory=True,           # agents remember context across tasks
        embedder={
            "provider": "huggingface",
            "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
        }
    )

    result = fd_crew.kickoff(inputs=user_input)
    return {"report": str(result), "raw_tasks": [str(t) for t in [t1_rates, t2_market, t3_optimize, t4_tax, t5_advise]]}


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FD PORTFOLIO OPTIMIZER — CREW AI SYSTEM")
    print("  6 Agents · Groq LLM · PSO Algorithm")
    print("="*60 + "\n")

    user_request = {
        "amount": 1000000,
        "risk_profile": "moderate",
        "tenure_months": 12,
        "name": "Demo User"
    }

    print(f"📥 User Request: {json.dumps(user_request, indent=2)}\n")
    result = run_fd_crew(user_request)
    print("\n" + "="*60)
    print("📊 FINAL PORTFOLIO REPORT")
    print("="*60)
    print(result["report"])
