"""
FD Portfolio Optimizer — Hybrid AI System
PSO algorithm (pure Python) + Groq LLM for advisory text.
Avoids CrewAI token overhead; works within Groq free tier (6k TPM).
"""

import os
import sys
import json

# Fix Windows emoji encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from agents.pso_optimizer import _run_pso_optimization
from agents.comparator_agent import _compare_investment_alternatives


def _get_groq_advice(user_input: dict, pso_data: dict) -> str:
    """Single compact Groq LLM call — ~500 tokens total, well within free tier."""
    try:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "Tip: Split investments across multiple banks for DICGC insurance protection. Book now while rates are near cycle peak."

        summary = pso_data["summary"]
        top_banks = [a for a in pso_data["allocation"] if a["weight_percent"] > 3][:3]
        top_str = ", ".join(
            f"{a['bank_name']} {a['weight_percent']:.0f}%@{a['interest_rate']}%"
            for a in top_banks
        )

        prompt = (
            f"FD portfolio advisor. Give 3 short, actionable tips.\n"
            f"Investor: {user_input.get('name','Investor')} | Risk: {user_input.get('risk_profile','moderate')} | "
            f"Amount: Rs{user_input.get('amount',1000000):,.0f} | Tenure: {user_input.get('tenure_months',12)} months\n"
            f"Top allocations: {top_str}\n"
            f"Return: {summary['expected_annual_return_pct']}% p.a.\n"
            f"Be brief, warm, India-specific. 3 bullet points only."
        )

        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        return f"Book FDs now — rates are near their peak. Split across banks to maximise DICGC coverage. (Advisory LLM note: {e})"


def run_fd_crew(user_input: dict) -> dict:
    """
    Hybrid pipeline:
      Agent 1 — Data Collector  : embedded bank data (no LLM needed)
      Agent 2 — PSO Optimizer   : pure Python algorithm (no LLM needed)
      Agent 3 — Comparator      : FD vs Alternatives (no LLM needed)
      Agent 4 — User Advisor    : single compact Groq LLM call (~500 tokens)
    """
    # ── Agent 1: Data (already baked into PSO) ──────────────────────
    pso_params = json.dumps({
        "total_amount": user_input.get("amount", 1000000),
        "risk_profile": user_input.get("risk_profile", "moderate"),
        "tenure_months": user_input.get("tenure_months", 12),
    })

    # ── Agent 2: PSO Optimization ────────────────────────────────────
    pso_data = json.loads(_run_pso_optimization(pso_params))

    # ── Agent 3: FD vs Alternatives Comparator (runs after PSO) ──────
    # Default tax_slab_pct to 30% if not provided by caller
    user_input.setdefault("tax_slab_pct", 30)
    comparison_result = None
    try:
        comparison_result = _compare_investment_alternatives(user_input, pso_data)
    except Exception as e:
        print(f"[Comparator] Non-fatal error — skipping comparison section: {e}")

    # ── Agent 4: AI Advisory (single LLM call) ───────────────────────
    advice = _get_groq_advice(user_input, pso_data)

    # ── Format final report ──────────────────────────────────────────
    s = pso_data["summary"]
    name = user_input.get("name", "Investor")
    tenure = user_input.get("tenure_months", 12)

    lines = [
        f"FD PORTFOLIO OPTIMIZER — AI REPORT",
        f"====================================",
        f"Investor : {name}",
        f"Amount   : Rs{s['total_investment']:,.0f}",
        f"Risk     : {s['risk_profile'].title()}",
        f"Tenure   : {tenure} months",
        f"",
        f"OPTIMISED ALLOCATION  (PSO · 60 particles · 200 iterations)",
        f"{'-'*62}",
        f"{'Bank':<24} {'Weight':>7} {'Rate':>6} {'Amount':>12} {'Maturity':>12}",
        f"{'-'*62}",
    ]

    for a in pso_data["allocation"]:
        if a["weight_percent"] > 2:
            lines.append(
                f"{a['bank_name']:<24} {a['weight_percent']:>6.1f}% {a['interest_rate']:>5.2f}%"
                f" Rs{a['allocated_amount']:>10,.0f} Rs{a['maturity_amount']:>10,.0f}"
            )

    lines += [
        f"{'-'*62}",
        f"",
        f"PORTFOLIO SUMMARY",
        f"  Total Investment : Rs{s['total_investment']:,.0f}",
        f"  Interest Earned  : Rs{s['total_interest_earned']:,.0f}",
        f"  Maturity Amount  : Rs{s['total_maturity_amount']:,.0f}",
        f"  Annual Return    : {s['expected_annual_return_pct']:.2f}% p.a.",
        f"  DICGC Compliant  : {'Yes' if s['dicgc_fully_compliant'] else 'Partial'}",
        f"",
        f"AI ADVISOR TIPS",
        f"================",
        advice,
        f"",
    ]

    # ── Comparator section (appended after PSO report) ────────────────
    if comparison_result:
        lines += [
            comparison_result["table_text"],
            comparison_result["recommendation"],
            f"",
        ]

    lines += [
        f"[Powered by PSO Algorithm + Groq Llama 3.1 8B + FD Comparator]",
    ]

    report = "\n".join(lines)
    return {
        "report": report,
        "pso_data": pso_data,
        "comparison": comparison_result,
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   FD PORTFOLIO OPTIMIZER — HYBRID AI SYSTEM")
    print("   PSO Algorithm + Groq LLM Advisory")
    print("=" * 60 + "\n")

    user_request = {
        "amount": 1000000,
        "risk_profile": "moderate",
        "tenure_months": 12,
        "name": "Demo User",
        "tax_slab_pct": 30,
    }

    print(f"User Request:\n{json.dumps(user_request, indent=2)}\n")
    result = run_fd_crew(user_request)

    print("\n" + "=" * 60)
    print("FINAL PORTFOLIO REPORT")
    print("=" * 60)
    print(result["report"])
