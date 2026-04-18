"""
Agent 2: Rate Decision Agent
Advises on timing: "Book now or wait?"
Uses RBI trends, inflation, market signals
"""

from crewai import Agent
from crewai.tools import tool
import json
from datetime import datetime


def _analyze_rate_timing(amount: float, tenure: int) -> str:
    """Internal logic for rate timing decision"""
    
    # Simulated market indicators (in production, call RBI API)
    current_date = datetime.now()
    month = current_date.month
    
    # Market analysis based on seasonal patterns
    # RBI typically hikes in Q1, cuts in Q3
    indicators = {
        "rbi_policy_rate": 6.5,  # Current (simulated)
        "inflation_rate": 4.8,   # Current (simulated)
        "market_trend": "Rates near peak",
        "season": "Post-peak rates"
    }
    
    analysis = {
        "amount": amount,
        "tenure_months": tenure,
        "current_rates": "8.2-8.5% (good)",
        "market_analysis": indicators,
        "decision": "",
        "confidence": "",
        "reasoning": ""
    }
    
    # Decision logic
    if indicators["inflation_rate"] > 5.0:
        analysis["decision"] = "WAIT - Inflation likely to trigger rate cuts"
        analysis["confidence"] = "60%"
        analysis["reasoning"] = f"Inflation at {indicators['inflation_rate']}% is high. RBI may cut rates in Q2-Q3."
    elif indicators["rbi_policy_rate"] >= 6.5:
        analysis["decision"] = "BOOK NOW - Rates at cycle peak"
        analysis["confidence"] = "85%"
        analysis["reasoning"] = "RBI policy rate at 6.5% (high). Current FD rates of 8.2-8.5% are near their peak."
    else:
        analysis["decision"] = "BOOK NOW - Stable high rates"
        analysis["confidence"] = "75%"
        analysis["reasoning"] = "FD rates are attractive and stable. Good time to lock in returns."
    
    # Amount-based urgency
    if amount >= 2500000:
        analysis["urgency"] = f"HIGH - Large amount (Rs {amount:,.0f}) should be invested before rates drop"
    elif amount >= 1000000:
        analysis["urgency"] = f"MEDIUM - Reasonable amount, can consider 2-3 week window"
    else:
        analysis["urgency"] = f"LOW - Small amount, you have time to decide"
    
    return json.dumps(analysis, indent=2)


@tool("rate_timing_decision")
def rate_timing_decision(data: str) -> str:
    """
    Analyze market conditions and recommend: Book now or wait?
    
    Considers:
    - RBI policy rate and trends
    - Current inflation signals
    - Current FD rate levels (peak/trough)
    - Your investment amount and tenure
    - Seasonal patterns
    
    Args:
        data: JSON with amount and tenure_months
    
    Returns:
        Timing recommendation with confidence and reasoning
    """
    try:
        input_data = json.loads(data) if isinstance(data, str) else data
        amount = float(input_data.get("amount", 1000000))
        tenure = int(input_data.get("tenure_months", 12))
        
        return _analyze_rate_timing(amount, tenure)
    except Exception as e:
        return json.dumps({"error": str(e)})


def build_rate_decision_agent(llm) -> Agent:
    """Create Rate Decision Agent"""
    return Agent(
        role="Market Timing & Rate Analysis Expert",
        goal="Determine optimal timing to book FDs based on market indicators",
        backstory=(
            "You are an RBI analyst and FD market expert. "
            "You track RBI policy rates, inflation trends, and market cycles. "
            "You help investors decide when rates are at their peak and best time to lock in returns. "
            "You consider macro indicators like inflation, RBI stance, and seasonal patterns."
        ),
        tools=[rate_timing_decision],
        llm=llm,
        verbose=False
    )
