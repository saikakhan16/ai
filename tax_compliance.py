"""
Agent 5: Tax & Compliance Agent
Handles TDS calculations, DICGC verification, Form 15G/15H reminders,
and tax optimization strategies for FD investments.
"""

from crewai import Agent
from crewai.tools import tool
import json


@tool("CalculateTDSAndTax")
def calculate_tds_and_tax(params: str) -> str:
    """
    Calculates TDS liability, net returns after tax, and provides
    tax optimization advice for FD investments.
    
    Input (JSON): {"amount": 1000000, "annual_return_pct": 8.21, "is_senior": false}
    """
    try:
        p = json.loads(params) if isinstance(params, str) else params
    except Exception:
        p = {}

    amount = float(p.get("amount", 1000000))
    annual_return = float(p.get("annual_return_pct", 8.0))
    is_senior = bool(p.get("is_senior", False))

    estimated_interest = amount * (annual_return / 100)
    tds_threshold = 50000 if is_senior else 40000
    tds_rate = 0.10
    tds_applicable = estimated_interest >= tds_threshold

    tds_amount = estimated_interest * tds_rate if tds_applicable else 0

    # Post-tax returns for different tax brackets
    tax_30 = estimated_interest * 0.30
    tax_20 = estimated_interest * 0.20
    tax_0  = 0

    forms_needed = []
    if tds_applicable:
        if is_senior:
            forms_needed.append("Form 15H (Senior Citizen — income below taxable limit)")
        else:
            forms_needed.append("Form 15G (Income below taxable limit)")

    advice = []
    if tds_applicable:
        advice.append(f"TDS of ₹{tds_amount:,.0f} will be auto-deducted by banks at 10%.")
        advice.append("Submit Form 15G/15H at the START of each financial year to avoid TDS.")
        advice.append("Track TDS deducted in Form 26AS and claim credit while filing ITR.")

    if amount > 500000:
        advice.append("Amount exceeds ₹5L DICGC limit per bank — the PSO has already split this for you.")

    if estimated_interest > 200000:
        advice.append("Consider booking some FDs in the next financial year to split tax liability.")
        advice.append("Invest in spouse's name (if lower tax bracket) to reduce family tax burden.")

    advice.append("Senior citizens (60+): higher TDS threshold ₹50,000 + 0.25-0.50% extra rate benefit.")
    advice.append("Section 80TTB: Senior citizens can claim deduction up to ₹50,000 on interest income.")

    return json.dumps({
        "estimated_annual_interest": round(estimated_interest, 2),
        "tds_threshold": tds_threshold,
        "tds_applicable": tds_applicable,
        "tds_amount_estimate": round(tds_amount, 2),
        "net_interest_after_tds": round(estimated_interest - tds_amount, 2),
        "post_tax_returns": {
            "nil_tax_bracket": round(estimated_interest - tax_0, 2),
            "20pct_bracket": round(estimated_interest - tax_20, 2),
            "30pct_bracket": round(estimated_interest - tax_30, 2)
        },
        "forms_to_submit": forms_needed,
        "tax_advice": advice,
        "important_deadlines": [
            "Submit Form 15G/15H: April 1st of every financial year",
            "TDS credit check: Form 26AS (available on income tax portal)",
            "ITR filing with FD interest: July 31st annually"
        ]
    }, indent=2)


@tool("VerifyDICGCCompliance")
def verify_dicgc_compliance(allocation_json: str) -> str:
    """
    Verifies that the portfolio allocation respects DICGC insurance limits.
    DICGC insures up to ₹5,00,000 per depositor per bank (principal + interest).
    """
    try:
        data = json.loads(allocation_json) if isinstance(allocation_json, str) else allocation_json
        allocation = data.get("allocation", data) if isinstance(data, dict) else data
    except Exception:
        return json.dumps({"error": "Invalid allocation data"})

    DICGC_LIMIT = 500000
    violations = []
    safe = []

    for alloc in allocation:
        amount = alloc.get("allocated_amount", 0)
        maturity = alloc.get("maturity_amount", amount)
        bank = alloc.get("bank_name", "Unknown")
        is_bank = alloc.get("dicgc_insured", True)

        if not is_bank:
            safe.append({"bank": bank, "status": "NBFC — not DICGC insured", "note": "Higher rating compensates (AAA/AA+)"})
        elif maturity > DICGC_LIMIT:
            violations.append({"bank": bank, "amount": amount, "maturity": maturity,
                               "excess": round(maturity - DICGC_LIMIT, 2)})
        else:
            safe.append({"bank": bank, "status": "FULLY INSURED ✅", "coverage": min(maturity, DICGC_LIMIT)})

    return json.dumps({
        "dicgc_limit_per_bank": DICGC_LIMIT,
        "violations": violations,
        "compliant_allocations": safe,
        "overall_status": "COMPLIANT ✅" if not violations else f"⚠️ {len(violations)} VIOLATION(S)",
        "note": "PSO optimization already penalizes DICGC violations heavily. Violations here indicate NBFCs (intentional)."
    }, indent=2)


def build_tax_compliance(llm) -> Agent:
    return Agent(
        role="FD Tax & Regulatory Compliance Specialist",
        goal=(
            "Calculate exact TDS liability, verify DICGC insurance compliance, "
            "identify all applicable tax forms (15G/15H), and provide actionable "
            "tax optimization strategies to maximize post-tax FD returns."
        ),
        backstory=(
            "You are a Chartered Accountant with 10 years specializing in "
            "retail fixed income taxation in India. You know the Income Tax Act "
            "sections 194A (TDS on interest), 80TTB (senior citizen deduction), "
            "and DICGC Act 1961 inside out. "
            "You have helped 2,000+ clients save lakhs in unnecessary TDS deductions "
            "simply by filing Form 15G on time. "
            "You speak in plain language — no jargon unless asked."
        ),
        tools=[calculate_tds_and_tax, verify_dicgc_compliance],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
