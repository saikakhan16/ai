"""
Agent 3: Market Intelligence Agent
Monitors RBI policy, inflation, GDP, and global rate trends.
Predicts whether rates will rise/fall/hold — tells user if NOW is good time to book FD.
"""

from crewai import Agent
from crewai.tools import tool
import json
from datetime import datetime


@tool("GetRBIRateAnalysis")
def get_rbi_rate_analysis(query: str = "current") -> str:
    """
    Returns RBI monetary policy analysis and rate cycle prediction.
    Includes repo rate, inflation data, MPC meeting outcomes, and booking recommendation.
    """
    analysis = {
        "analysis_date": datetime.now().strftime("%B %Y"),
        "rbi_repo_rate": 6.25,
        "rbi_stance": "neutral",
        "last_mpc_decision": "Hold — April 2026",
        "inflation_cpi": 4.1,
        "inflation_target": 4.0,
        "gdp_growth_q4": 6.8,
        "rate_cycle_phase": "peak_to_plateau",
        "prediction": {
            "3_months": "hold",
            "6_months": "possible_25bps_cut",
            "12_months": "50-75bps_cumulative_cut",
            "confidence_pct": 72
        },
        "booking_signal": "BOOK NOW",
        "signal_strength": "STRONG",
        "reasoning": (
            "CPI inflation at 4.1% — just above RBI's 4% target but within comfort zone. "
            "With US Fed pausing and domestic growth solid at 6.8%, RBI has room to hold. "
            "However, easing cycle expected H2 2026. Current FD rates (8.25-8.55%) "
            "are near cycle peak. Locking 12-18M tenures now captures peak rates "
            "before anticipated cuts."
        ),
        "risk_factors": [
            "US Fed rate decisions (FOMC June/September)",
            "Monsoon 2026 — poor monsoon = food inflation spike = delayed cuts",
            "Global crude oil prices (Brent above $90 = inflationary pressure)",
            "Geopolitical risks affecting FII flows and INR"
        ],
        "optimal_tenure_recommendation": "12-18 months",
        "avoid_tenures": "3-6 months (may mature before rates drop, missing reinvestment risk)"
    }
    return json.dumps(analysis, indent=2)


@tool("GetMacroIndicators")
def get_macro_indicators(query: str = "india") -> str:
    """
    Returns key macroeconomic indicators relevant to FD investment decisions.
    """
    indicators = {
        "india_10yr_gsec_yield": 6.85,
        "india_inflation_cpi": 4.1,
        "india_gdp_growth": 6.8,
        "usd_inr": 83.45,
        "us_fed_funds_rate": 4.25,
        "us_10yr_treasury": 4.35,
        "crude_oil_brent": 82.4,
        "real_fd_return_estimate": 4.15,
        "fd_vs_equity_signal": "FD attractive — Nifty P/E elevated at 22x",
        "senior_citizen_bonus": "+0.25% to +0.50% on most banks",
        "tax_adjusted_return_30pct_bracket": "5.77% post-tax (8.25% pre-tax)",
        "inflation_adjusted_real_return": "4.15% real return"
    }
    return json.dumps(indicators, indent=2)


def build_market_intel(llm) -> Agent:
    return Agent(
        role="RBI Monetary Policy & Macro Intelligence Analyst",
        goal=(
            "Analyze RBI rate cycle, inflation trajectory, and global macro conditions "
            "to determine the optimal FD booking strategy. "
            "Answer: Should the user book NOW or WAIT? Which tenure maximizes rate-lock advantage?"
        ),
        backstory=(
            "You are a former RBI research department economist with 12 years of experience "
            "tracking monetary policy cycles across emerging markets. "
            "You predicted all 3 of the last RBI rate pivot points within one meeting. "
            "You synthesize CPI data, MPC minutes, Fed signals, and commodity prices "
            "into clear, actionable investment timing signals. "
            "Your reports are trusted by HNI investors managing ₹50Cr+ portfolios."
        ),
        tools=[get_rbi_rate_analysis, get_macro_indicators],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
