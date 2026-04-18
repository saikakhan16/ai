"""
Agent 1: Bank Recommendation Agent
Suggests best banks based on tenure, provides reasoning
Uses LLM to give personalized bank recommendations
"""

from crewai import Agent
from crewai.tools import tool
import json


def _recommend_banks_by_tenure(tenure_months: str, top_banks: list) -> str:
    """Internal logic for bank recommendations"""
    tenure = int(tenure_months)
    banks_data = {
        "banks": top_banks,
        "analysis": {}
    }
    
    if tenure <= 6:
        banks_data["analysis"] = {
            "tenure_category": "Short-term (3-6 months)",
            "recommendation": "Bajaj Finance & Shriram Finance",
            "reason": "Higher liquidity, flexible renewal options",
            "best_for": "Emergency fund, near-term goals"
        }
    elif tenure <= 12:
        banks_data["analysis"] = {
            "tenure_category": "Medium-term (9-12 months)",
            "recommendation": "Mix of NBFCs (Bajaj, Shriram) + SFBs (Suryoday, Unity)",
            "reason": "Balance of rates and safety, DICGC protection on SFBs",
            "best_for": "Standard investment, annual goals"
        }
    else:
        banks_data["analysis"] = {
            "tenure_category": "Long-term (18-24 months)",
            "recommendation": "Prioritize SFBs (Suryoday, Utkarsh) + Top NBFCs",
            "reason": "Highest rates available, compound interest benefit",
            "best_for": "Long-term wealth building, locked-in strategy"
        }
    
    return json.dumps(banks_data, indent=2)


@tool("bank_recommendation")
def bank_recommendation(data: str) -> str:
    """
    Recommend banks based on tenure and rates.
    
    Analyzes top banks and suggests which ones are best for:
    - Short tenure (3-6m) → Liquidity + flexibility
    - Medium tenure (9-12m) → Standard balance
    - Long tenure (18-24m) → Maximum returns + compounding
    
    Args:
        data: JSON with tenure_months and top_banks list
    
    Returns:
        Bank recommendations with reasoning
    """
    try:
        input_data = json.loads(data) if isinstance(data, str) else data
        tenure = str(input_data.get("tenure_months", "12"))
        top_banks = input_data.get("top_banks", [])
        
        return _recommend_banks_by_tenure(tenure, top_banks)
    except Exception as e:
        return json.dumps({"error": str(e)})


def build_bank_recommendation_agent(llm) -> Agent:
    """Create Bank Recommendation Agent"""
    return Agent(
        role="Bank Recommendation Specialist",
        goal="Recommend the best banks based on tenure, rates, and safety",
        backstory=(
            "You are a Fixed Deposit expert who understands Indian banking landscape. "
            "You know which banks are best for different time horizons. "
            "You consider DICGC protection, liquidity, renewal terms, and rates."
        ),
        tools=[bank_recommendation],
        llm=llm,
        verbose=False
    )
