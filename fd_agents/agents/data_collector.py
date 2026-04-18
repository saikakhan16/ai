"""
Agent 2: Data Collector
Fetches and normalizes live FD rates from all Blostem partner banks.
Uses real bank data + simulated live fetch (swap with real scraper in prod).
"""

from crewai import Agent
from crewai.tools import tool
import json
from datetime import datetime


# ── TOOL FUNCTIONS ────────────────────────────────────────────────────────────

def _get_all_banks() -> list:
    """Internal helper to get bank data"""
    return [
        {
            "id": "suryoday", "name": "Suryoday Small Finance Bank",
            "type": "Small Finance Bank", "rating": "AA", "dicgc": True,
            "rates": {"3": 6.75, "6": 7.25, "9": 7.50, "12": 8.25, "18": 8.50, "24": 8.35}
        },
        {
            "id": "unity", "name": "Unity Small Finance Bank",
            "type": "Small Finance Bank", "rating": "AA", "dicgc": True,
            "rates": {"3": 6.50, "6": 7.00, "9": 7.35, "12": 8.15, "18": 8.40, "24": 8.20}
        },
        {
            "id": "utkarsh", "name": "Utkarsh Small Finance Bank",
            "type": "Small Finance Bank", "rating": "AA", "dicgc": True,
            "rates": {"3": 6.60, "6": 7.10, "9": 7.40, "12": 8.10, "18": 8.30, "24": 8.15}
        },
        {
            "id": "shivalik", "name": "Shivalik Small Finance Bank",
            "type": "Small Finance Bank", "rating": "A+", "dicgc": True,
            "rates": {"3": 6.40, "6": 6.90, "9": 7.25, "12": 8.00, "18": 8.20, "24": 8.00}
        },
        {
            "id": "shriram", "name": "Shriram Finance",
            "type": "NBFC", "rating": "AA+", "dicgc": False,
            "rates": {"3": 7.00, "6": 7.50, "9": 7.75, "12": 8.30, "18": 8.45, "24": 8.50}
        },
        {
            "id": "bajaj", "name": "Bajaj Finance",
            "type": "NBFC", "rating": "AAA", "dicgc": False,
            "rates": {"3": 7.15, "6": 7.60, "9": 7.80, "12": 8.35, "18": 8.50, "24": 8.55}
        },
        {
            "id": "mahindra", "name": "Mahindra Finance",
            "type": "NBFC", "rating": "AA+", "dicgc": False,
            "rates": {"3": 6.90, "6": 7.40, "9": 7.65, "12": 8.20, "18": 8.35, "24": 8.40}
        },
        {
            "id": "jana", "name": "Jana Small Finance Bank",
            "type": "Small Finance Bank", "rating": "A+", "dicgc": True,
            "rates": {"3": 6.30, "6": 6.85, "9": 7.20, "12": 7.90, "18": 8.10, "24": 7.95}
        }
    ]


def _fetch_live_fd_rates(query: str = "all") -> str:
    """Internal function to fetch rates"""
    rates_data = {
        "fetched_at": datetime.now().isoformat(),
        "source": "Blostem Partner Bank Network",
        "banks": _get_all_banks()
    }
    return json.dumps(rates_data, indent=2)


def _compare_bank_rates(tenure_months: str = "12") -> str:
    """Internal function to compare banks"""
    tenure = str(tenure_months).strip()
    banks = _get_all_banks()
    comparison = []
    for b in banks:
        rate = b["rates"].get(tenure, b["rates"].get("12", 7.0))
        comparison.append({
            "bank": b["name"], "type": b["type"], "rating": b["rating"],
            "rate": rate, "dicgc_protected": b["dicgc"]
        })
    comparison.sort(key=lambda x: x["rate"], reverse=True)
    return json.dumps({"tenure_months": tenure, "ranked_banks": comparison}, indent=2)


# CrewAI Tool versions (for agents)
@tool("fetch_live_fd_rates")
def fetch_live_fd_rates(query: str = "all") -> str:
    """
    Fetches current Fixed Deposit rates from all Blostem partner banks.
    Returns structured JSON with rates for all tenures.
    """
    return _fetch_live_fd_rates(query)


@tool("compare_bank_rates")
def compare_bank_rates(tenure_months: str = "12") -> str:
    """
    Returns a ranked comparison of all banks for a specific tenure.
    Pass tenure in months as a string: '3', '6', '9', '12', '18', or '24'.
    """
    return _compare_bank_rates(tenure_months)
    comparison = []
    for b in banks:
        rate = b["rates"].get(tenure, b["rates"].get("12", 7.0))
        comparison.append({
            "bank": b["name"], "type": b["type"], "rating": b["rating"],
            "rate": rate, "dicgc_protected": b["dicgc"]
        })
    comparison.sort(key=lambda x: x["rate"], reverse=True)
    return json.dumps({"tenure_months": tenure, "ranked_banks": comparison}, indent=2)


# ── AGENT ─────────────────────────────────────────────────────────────────────

def build_data_collector(llm) -> Agent:
    return Agent(
        role="FD Rate Intelligence Analyst",
        goal=(
            "Fetch the latest Fixed Deposit rates from all 8 Blostem partner banks, "
            "validate the data for accuracy, and present a clean structured dataset "
            "for the optimization engine to use."
        ),
        backstory=(
            "You are a meticulous data analyst who has built rate-monitoring systems "
            "for three major wealth management firms. You know every Small Finance Bank "
            "and NBFC in India, understand the difference between DICGC-insured deposits "
            "and corporate FDs, and can spot anomalies in rate data instantly. "
            "You deliver clean, validated JSON — never guesses."
        ),
        tools=[fetch_live_fd_rates, compare_bank_rates],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
