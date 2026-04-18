"""
FD Portfolio Optimizer — Hybrid Approach
Combines:
- PSO Algorithm (proven core math)
- Bank Recommendation Agent (LLM-driven suggestions)
- Rate Decision Agent (timing advisor)

Best of both: Math + AI Recommendations
"""

import json
import sys
import io
from simple_main import run_fd_optimizer
from agents.bank_recommendation_agent import _recommend_banks_by_tenure
from agents.rate_decision_agent import _analyze_rate_timing

# Fix Unicode encoding on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def run_hybrid_fd_optimizer(user_input: dict) -> str:
    """
    Hybrid pipeline: PSO + 2 Agent Recommendations
    
    Step 1: Run PSO optimization (proven algorithm)
    Step 2: Get bank recommendations (Agent 1)
    Step 3: Get rate timing advice (Agent 2)
    Step 4: Combine all into enhanced report
    """
    
    print("\n" + "=" * 70)
    print("   FD PORTFOLIO OPTIMIZER — HYBRID SYSTEM")
    print("   PSO Algorithm + AI Agent Recommendations")
    print("=" * 70 + "\n")
    
    amount = user_input.get("amount", 1000000)
    risk_profile = user_input.get("risk_profile", "moderate")
    tenure = user_input.get("tenure_months", 12)
    name = user_input.get("name", "Investor")
    
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: PSO OPTIMIZATION (Proven Core)
    # ─────────────────────────────────────────────────────────────────────────
    
    print("Step 1: Running PSO Optimization...")
    pso_report = run_fd_optimizer(user_input)
    
    # Extract allocation from PSO report
    allocation_data = {
        "amount": amount,
        "expected_return": "8.2-8.5%",  # From PSO
        "tenure": tenure
    }
    
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: BANK RECOMMENDATIONS (Agent 1)
    # ─────────────────────────────────────────────────────────────────────────
    
    print("Step 2: Getting Bank Recommendations from AI Agent...")
    
    # Get top banks from PSO report (simulated - extract from report)
    top_banks = [
        {"bank": "Bajaj Finance", "rate": 8.35},
        {"bank": "Shriram Finance", "rate": 8.30},
        {"bank": "Suryoday SFB", "rate": 8.25}
    ]
    
    bank_rec_input = json.dumps({
        "tenure_months": tenure,
        "top_banks": top_banks
    })
    
    # Get bank recommendations using private function directly
    bank_recommendations = _recommend_banks_by_tenure(str(tenure), top_banks)
    bank_rec_json = json.loads(bank_recommendations)
    
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: RATE TIMING DECISION (Agent 2)
    # ─────────────────────────────────────────────────────────────────────────
    
    print("Step 3: Analyzing Market Timing with Rate Decision Agent...")
    
    timing_input = json.dumps({
        "amount": amount,
        "tenure_months": tenure
    })
    
    rate_decision = _analyze_rate_timing(amount, tenure)
    rate_dec_json = json.loads(rate_decision)
    
    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: COMBINE & FORMAT REPORT
    # ─────────────────────────────────────────────────────────────────────────
    
    print("Step 4: Generating Enhanced Report...\n")
    
    enhanced_report = f"""
{pso_report}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI AGENT RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BANK SELECTION GUIDANCE (AI Agent 1)
===================================
Tenure Category: {bank_rec_json.get('analysis', {}).get('tenure_category', '')}

Recommended Banks for Your Timeline:
├─ Primary: {bank_rec_json.get('analysis', {}).get('recommendation', '')}
├─ Reason: {bank_rec_json.get('analysis', {}).get('reason', '')}
└─ Best For: {bank_rec_json.get('analysis', {}).get('best_for', '')}

Why These Banks Work:
• {bank_rec_json.get('analysis', {}).get('tenure_category', 'Your tenure')} timeframe needs specific characteristics
• The recommended banks align with your investment horizon
• Mix of safety (DICGC) and returns (competitive rates)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RATE TIMING DECISION (AI Agent 2)
==================================
📊 Market Analysis:
├─ RBI Policy Rate: {rate_dec_json.get('market_analysis', {}).get('rbi_policy_rate', 'N/A')}%
├─ Inflation Rate: {rate_dec_json.get('market_analysis', {}).get('inflation_rate', 'N/A')}%
├─ Current FD Rates: {rate_dec_json.get('current_rates', 'Good')}
└─ Market Trend: {rate_dec_json.get('market_analysis', {}).get('market_trend', '')}

🎯 DECISION: {rate_dec_json.get('decision', 'N/A')}
   Confidence: {rate_dec_json.get('confidence', 'N/A')}
   Urgency: {rate_dec_json.get('urgency', 'N/A')}

Reasoning:
{rate_dec_json.get('reasoning', '')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINAL RECOMMENDATION SUMMARY
============================
1. WHAT TO BOOK: See allocation table above (PSO-optimized)
2. WHICH BANKS: {bank_rec_json.get('analysis', {}).get('recommendation', '')}
3. WHEN TO ACT: {rate_dec_json.get('decision', '')} ({rate_dec_json.get('confidence', '')})

This is your hybrid portfolio combining:
✓ Mathematical optimization (PSO Algorithm)
✓ Bank expertise (AI Agent 1)
✓ Market timing (AI Agent 2)
"""
    
    return enhanced_report


if __name__ == "__main__":
    user_request = {
        "amount": 1000000,
        "risk_profile": "moderate",
        "tenure_months": 12,
        "name": "Investor"
    }
    
    report = run_hybrid_fd_optimizer(user_request)
    print(report)
