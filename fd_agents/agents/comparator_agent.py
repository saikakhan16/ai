"""
Agent 7: FD vs Alternatives Comparator Agent
Compares Fixed Deposits against Debt MF, SGB, RD, and PPF.
Calculates pre-tax, post-tax (at user's slab), and inflation-adjusted real returns.
"""

from crewai import Agent
from crewai.tools import tool
import json
import urllib.request


# ── CPI FETCH ────────────────────────────────────────────────────────────────

def _fetch_cpi_rate() -> float:
    """
    Try to fetch latest CPI from data.gov.in.
    Falls back to 5.5% if the request fails or returns unexpected data.
    """
    try:
        # data.gov.in CPI combined index endpoint (no key needed for basic access)
        url = (
            "https://api.data.gov.in/resource/b49b6e1a-2a64-4c1b-a898-5c85b3fb99f7"
            "?format=json&limit=1"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "FDOptimizer/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            records = data.get("records", [])
            if records:
                for field in ["cpi_combined", "value", "cpi", "index_number"]:
                    if field in records[0]:
                        raw = float(records[0][field])
                        # If it looks like an index level (~130-200), convert to YoY ~%
                        if 2.0 <= raw <= 15.0:
                            print(f"[Comparator] Fetched CPI: {raw:.1f}% from data.gov.in")
                            return raw
    except Exception as e:
        print(f"[Comparator] CPI fetch failed ({e}); using fallback 5.5%")
    return 5.5


# ── CALCULATION HELPERS ──────────────────────────────────────────────────────

def _after_slab_tax(pre_tax_pct: float, tax_rate_pct: float) -> float:
    """Apply income-slab tax rate to a pre-tax return percentage."""
    return pre_tax_pct * (1.0 - tax_rate_pct / 100.0)


def _real_return(post_tax_pct: float, inflation_pct: float) -> float:
    """
    Fisher equation: real return = ((1+nominal)/(1+inflation)) - 1
    Both inputs and output are in percentage points.
    """
    return ((1.0 + post_tax_pct / 100.0) / (1.0 + inflation_pct / 100.0) - 1.0) * 100.0


# ── CORE COMPARISON LOGIC ────────────────────────────────────────────────────

def _compare_investment_alternatives(user_input: dict, pso_data: dict) -> dict:
    """
    Core comparison engine — called directly by main.py (no LLM needed).

    Returns a dict with:
      - 'table_text'     : formatted comparison table string
      - 'recommendation' : tailored recommendation string
      - 'rows'           : list of dicts (one per instrument)
      - 'inflation_used' : float
      - 'tax_slab_used'  : int
    """
    print("[Comparator] Starting FD vs Alternatives analysis...")

    tax_slab = int(user_input.get("tax_slab_pct", 30))
    tenure_months = int(user_input.get("tenure_months", 12))
    risk_profile = user_input.get("risk_profile", "moderate")

    inflation = _fetch_cpi_rate()

    # Best FD rate comes from PSO result
    fd_rate = float(
        pso_data.get("summary", {}).get("expected_annual_return_pct", 7.5)
    )

    # SGB constants (RBI latest issue)
    SGB_GOLD_RATE = 8.05   # gold price appreciation component — tax-free at maturity
    SGB_COUPON    = 2.50   # government coupon — taxed at slab

    # Instrument definitions
    instruments = [
        {
            "name":      "FD (Best)",
            "pre_tax":   fd_rate,
            "tax_type":  "slab",
            "risk":      2,
            "liquidity": 7,
            "horizon":   "short / medium-term",
            "notes":     "DICGC insured up to Rs5L per bank",
        },
        {
            "name":      "Debt Mutual Fund",
            "pre_tax":   7.2,
            "tax_type":  "slab",        # post-Apr 2023: no indexation, taxed at slab
            "risk":      4,
            "liquidity": 9,
            "horizon":   "short / medium-term",
            "notes":     "Taxed at slab since Apr 2023; no lock-in",
        },
        {
            "name":           "SGB",
            "pre_tax":        SGB_GOLD_RATE + SGB_COUPON,
            "tax_type":       "sgb",    # gold gain tax-free at maturity; coupon taxed
            "sgb_gold_rate":  SGB_GOLD_RATE,
            "sgb_coupon":     SGB_COUPON,
            "risk":           3,
            "liquidity":      4,
            "horizon":        "long-term (8 yr maturity)",
            "notes":          "Gold appreciation tax-free; 2.5% coupon taxed at slab",
        },
        {
            "name":      "Recurring Deposit",
            "pre_tax":   7.0,
            "tax_type":  "slab",
            "risk":      2,
            "liquidity": 6,
            "horizon":   "short / medium-term",
            "notes":     "Monthly commitment; taxed like FD",
        },
        {
            "name":      "PPF",
            "pre_tax":   7.1,
            "tax_type":  "exempt",      # EEE — fully tax-free
            "risk":      1,
            "liquidity": 3,
            "horizon":   "long-term (15 yr lock-in)",
            "notes":     "EEE; partial withdrawal from yr 7 only",
        },
    ]

    rows = []
    for inst in instruments:
        pre = inst["pre_tax"]

        if inst["tax_type"] == "exempt":
            post = pre
        elif inst["tax_type"] == "sgb":
            # Gold capital gain is tax-free; coupon taxed at slab
            post = inst["sgb_gold_rate"] + _after_slab_tax(inst["sgb_coupon"], tax_slab)
        else:
            post = _after_slab_tax(pre, tax_slab)

        real = _real_return(post, inflation)

        rows.append({
            "instrument":     inst["name"],
            "pre_tax_pct":    round(pre, 2),
            "post_tax_pct":   round(post, 2),
            "real_return_pct":round(real, 2),
            "risk_score":     inst["risk"],
            "liquidity_score":inst["liquidity"],
            "horizon":        inst["horizon"],
            "notes":          inst["notes"],
        })

    # ── Build table text ─────────────────────────────────────────────────────
    sep = "=" * 82
    dashes = "-" * 82
    table_lines = [
        "",
        "FD VS ALTERNATIVES COMPARISON",
        sep,
        f"Tax Slab : {tax_slab}%  |  Inflation (CPI) : {inflation:.1f}%  |"
        f"  Tenure : {tenure_months} months",
        dashes,
        f"{'Instrument':<22} {'Pre-tax':>8} {'Post-tax':>10}"
        f" {'Real Ret':>10} {'Risk':>6} {'Liquidity':>10}",
        dashes,
    ]
    for r in rows:
        table_lines.append(
            f"{r['instrument']:<22} {r['pre_tax_pct']:>7.2f}%"
            f" {r['post_tax_pct']:>9.2f}%"
            f" {r['real_return_pct']:>9.2f}%"
            f" {r['risk_score']:>4}/10"
            f" {r['liquidity_score']:>7}/10"
        )
    table_lines.append(dashes)

    # Footnotes
    table_lines += [
        "Notes:",
        "  FD (Best)        — DICGC insured up to Rs5L per bank; taxed at slab",
        "  Debt Mutual Fund — Taxed at income slab since Apr 2023 (no indexation)",
        "  SGB              — Gold appreciation tax-free at maturity; coupon taxed",
        "  Recurring Dep.   — Monthly contribution required; taxed like FD",
        "  PPF              — EEE status (exempt-exempt-exempt); 15 yr lock-in",
    ]
    table_text = "\n".join(table_lines)

    # ── Recommendation ───────────────────────────────────────────────────────
    fd_row  = next(r for r in rows if r["instrument"] == "FD (Best)")
    ppf_row = next(r for r in rows if r["instrument"] == "PPF")
    sgb_row = next(r for r in rows if r["instrument"] == "SGB")

    avoid = []
    if tenure_months < 84:
        avoid.append("PPF (15-year lock-in far exceeds your tenure)")
    if tenure_months < 96:
        avoid.append("SGB (8-year maturity; early exit at market discount)")

    if tenure_months <= 12:
        alloc_text = "FD: 60%, Debt MF: 40%"
        reason     = "liquidity + stable returns for short tenure"
    elif tenure_months <= 36:
        alloc_text = "FD: 40%, Debt MF: 30%, SGB: 30%"
        reason     = "balanced growth with inflation protection"
    else:
        alloc_text = "SGB: 40%, PPF: 30%, FD: 30%"
        reason     = "long-term wealth creation with maximum tax efficiency"

    avoid_str = "; ".join(avoid) if avoid else "None — all instruments suit your tenure"

    # Best real-return instrument overall
    best = max(rows, key=lambda r: r["real_return_pct"])

    rec_lines = [
        "",
        "INVESTMENT RECOMMENDATION",
        sep,
        f"Profile : {tax_slab}% tax bracket | {tenure_months}-month tenure"
        f" | {risk_profile.title()} risk",
        "",
        f"  Best allocation  : {alloc_text}",
        f"  Why              : {reason}",
        f"  Avoid            : {avoid_str}",
        "",
        f"  Highest real return: {best['instrument']} at"
        f" {best['real_return_pct']:.2f}% p.a. after tax & inflation",
        f"  FD advantage: predictable {fd_row['pre_tax_pct']:.2f}% pre-tax with DICGC safety",
        f"  FD real return: {fd_row['real_return_pct']:.2f}% p.a."
        f" (post {tax_slab}% tax & {inflation:.1f}% inflation)",
    ]
    if tax_slab == 30:
        rec_lines.append(
            "  Tax tip: PPF & SGB offer better post-tax returns for 30% bracket investors"
        )

    recommendation = "\n".join(rec_lines)

    print("[Comparator] Analysis complete.")
    return {
        "table_text":     table_text,
        "recommendation": recommendation,
        "rows":           rows,
        "inflation_used": inflation,
        "tax_slab_used":  tax_slab,
    }


# ── CREWAI TOOL WRAPPER ──────────────────────────────────────────────────────

@tool("compare_investment_alternatives")
def compare_investment_alternatives(params: str) -> str:
    """
    Compares Fixed Deposits against Debt MF, SGB, RD, and PPF.

    Input (JSON string):
    {
        "user_input": {
            "tax_slab_pct": 30,
            "tenure_months": 12,
            "risk_profile": "moderate"
        },
        "fd_annual_return_pct": 8.25
    }

    Returns a formatted comparison table plus a personalised recommendation.
    """
    try:
        p = json.loads(params) if isinstance(params, str) else params
    except Exception:
        p = {}

    user_input = p.get("user_input", {})
    fd_return  = float(p.get("fd_annual_return_pct", 7.5))
    mock_pso   = {"summary": {"expected_annual_return_pct": fd_return}}

    result = _compare_investment_alternatives(user_input, mock_pso)
    return result["table_text"] + "\n" + result["recommendation"]


# ── CREWAI AGENT BUILDER ─────────────────────────────────────────────────────

def build_comparator_agent(llm) -> Agent:
    """Build the CrewAI-compatible FD vs Alternatives Comparator Agent."""
    return Agent(
        role="Investment Alternatives Analyst",
        goal=(
            "Compare Fixed Deposits against Debt Mutual Funds, Sovereign Gold Bonds, "
            "Recurring Deposits, and PPF. Calculate pre-tax, post-tax, and "
            "inflation-adjusted real returns for the user's specific tax slab. "
            "Produce a clear comparison table and a concrete allocation recommendation "
            "tailored to the user's tenure and risk profile."
        ),
        backstory=(
            "You are a SEBI-registered Research Analyst specialising in fixed-income "
            "instruments. You track RBI policy, SEBI regulations, and CPI data daily. "
            "You have helped retail investors understand why tax efficiency matters as "
            "much as headline rates — a 7.1% PPF beats a 9% taxable FD for someone in "
            "the 30% bracket. Your comparisons are honest, data-driven, and bias-free."
        ),
        tools=[compare_investment_alternatives],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
