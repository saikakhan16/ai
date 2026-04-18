"""
FD Portfolio Optimizer — Simple Direct Pipeline (No CrewAI overhead)
Chains tools directly: Rates → Optimization → Report
Minimal token usage = no rate limiting issues
"""

import json
from agents.data_collector import _fetch_live_fd_rates, _compare_bank_rates
from agents.pso_optimizer import _run_pso_optimization
from agents.user_advisor import _generate_portfolio_report


def run_fd_optimizer(user_input: dict) -> str:
    """Direct pipeline without CrewAI agents - minimal token usage"""
    
    print("\n" + "=" * 60)
    print("   FD PORTFOLIO OPTIMIZER — SIMPLE PIPELINE")
    print("   Direct Tool Chain (No Agent Overhead)")
    print("=" * 60 + "\n")
    
    amount = user_input.get("amount", 1000000)
    risk_profile = user_input.get("risk_profile", "moderate")
    tenure = user_input.get("tenure_months", 12)
    name = user_input.get("name", "User")
    
    # Step 1: Fetch and compare rates
    print("Step 1: Fetching FD rates from all banks...")
    rates_result = _fetch_live_fd_rates("all")
    rates_data = json.loads(rates_result)
    print(f"  [OK] Fetched {len(rates_data['banks'])} banks")
    
    print(f"\nStep 2: Comparing banks for {tenure}-month tenure...")
    comparison_result = _compare_bank_rates(str(tenure))
    comparison = json.loads(comparison_result)
    print(f"  [OK] Top 3 banks identified")
    
    # Step 2: Run PSO optimization
    print(f"\nStep 3: Running PSO optimization (amount: Rs{amount:,}, risk: {risk_profile})...")
    pso_params = json.dumps({
        "total_amount": amount,
        "risk_profile": risk_profile,
        "tenure_months": tenure,
        "banks": rates_data["banks"]
    })
    optimization_result = _run_pso_optimization(pso_params)
    optimization = json.loads(optimization_result)
    print(f"  [OK] Optimal allocation found")
    print(f"  [OK] Expected annual return: {optimization['summary']['expected_annual_return_pct']}%")
    
    # Step 3: Generate report
    print(f"\nStep 4: Generating personalized report for {name}...")
    report_data = json.dumps({
        "user_name": name,
        "investment_amount": amount,
        "risk_profile": risk_profile,
        "tenure": tenure,
        "allocation": optimization["allocation"],
        "summary": optimization["summary"],
        "ladder": optimization["ladder_strategy"],
        "top_banks": comparison.get("ranked_banks", [])[:3]
    })
    report = _generate_portfolio_report(report_data)
    print(f"  [OK] Report generated")
    
    print("\n" + "=" * 60)
    print("FINAL PORTFOLIO REPORT")
    print("=" * 60)
    print(report)
    
    return report


if __name__ == "__main__":
    user_request = {
        "amount": 1000000,
        "risk_profile": "moderate",
        "tenure_months": 12,
        "name": "Demo User"
    }
    
    result = run_fd_optimizer(user_request)
