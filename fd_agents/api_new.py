"""
FD Portfolio Optimizer — REST API
Lightweight FastAPI using the proven simple_main.py pipeline
No CrewAI overhead — minimal token usage
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import re
import logging
from datetime import datetime
import traceback

from simple_main import run_fd_optimizer
from agents.bank_selector_agent import get_bank_recommendation
from agents.rate_decision_agent import get_rate_decision
from agents.comparator_agent import _compare_investment_alternatives

# ── LOGGING ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── FASTAPI APP ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="FD Portfolio Optimizer API",
    description="Optimizes Fixed Deposit allocation across 8 banks using PSO algorithm",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REQUEST/RESPONSE MODELS ────────────────────────────────────────────────────

class OptimizeRequest(BaseModel):
    """User's FD optimization request"""
    amount: float = Field(
        default=1000000, 
        ge=100000,
        le=100000000,
        description="Investment amount in Rs (min 1 Lakh, max 10 Cr)"
    )
    risk_profile: str = Field(
        default="moderate",
        description="conservative | moderate | aggressive"
    )
    tenure_months: int = Field(
        default=12,
        ge=3,
        le=24,
        description="Investment tenure in months (3-24)"
    )
    name: str = Field(
        default="Investor",
        description="Investor's name for personalized report"
    )
    tax_slab_pct: int = Field(
        default=30,
        description="Income tax slab percentage: 0, 5, 20, or 30"
    )

    class Config:
        example = {
            "amount": 1500000,
            "risk_profile": "moderate",
            "tenure_months": 12,
            "name": "Rajesh Kumar"
        }


class OptimizeResponse(BaseModel):
    """API response with optimization result"""
    model_config = {"populate_by_name": True}

    success: bool
    report: str
    bank_recommendation: str = ""
    rate_decision: str = ""
    allocation: Optional[list] = None
    summary: Optional[dict] = None
    comparison_rows: Optional[list] = None
    comparison_text: str = ""
    inflation_used: float = 5.5
    timestamp: str
    request_params: Dict[str, Any]
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str


# ── REPORT PARSERS ────────────────────────────────────────────────────────────

DICGC_LIMIT = 500_000
RATING_MAP  = {"bajaj": "AAA", "shriram": "AA+", "mahindra": "AA+",
               "suryoday": "AA", "unity": "AA", "utkarsh": "AA",
               "shivalik": "A+", "jana": "A+"}

def _parse_float(text: str, pattern: str) -> float:
    """Extract first float matching pattern from report text."""
    m = re.search(pattern, text)
    if not m: return 0.0
    return float(m.group(1).replace(",", ""))


def _parse_allocation_from_report(report: str, total_amount: float) -> list:
    """
    Parse allocation table from _generate_portfolio_report text.
    Line format: BankName             | Rs103,004 | 8.35% | Rs112,551
    """
    section = re.search(r'Bank Name \| Amount \| Rate \| Maturity\n-+\n([\s\S]*?)\n\nTotal', report)
    if not section:
        return []
    rows = []
    for line in section.group(1).strip().splitlines():
        m = re.match(r'^(.+?)\s*\|\s*Rs([\d,]+\.?\d*)\s*\|\s*([\d.]+)%\s*\|\s*Rs([\d,]+\.?\d*)$', line.strip())
        if not m:
            continue
        name    = m.group(1).strip()
        amount  = float(m.group(2).replace(",", ""))
        rate    = float(m.group(3))
        mat     = float(m.group(4).replace(",", ""))
        interest= mat - amount
        bid     = name.lower().split()[0]
        rows.append({
            "bank_name":       name,
            "bank_id":         bid,
            "allocated_amount":round(amount, 2),
            "weight_percent":  round(amount / total_amount * 100, 2) if total_amount else 0,
            "interest_rate":   rate,
            "interest_earned": round(interest, 2),
            "maturity_amount": round(mat, 2),
            "dicgc_insured":   amount <= DICGC_LIMIT,
            "rating":          RATING_MAP.get(bid, "A"),
        })
    rows.sort(key=lambda r: r["allocated_amount"], reverse=True)
    return rows


# ── API ENDPOINTS ──────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="3.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_portfolio(request: OptimizeRequest) -> OptimizeResponse:
    """
    Main endpoint: Optimize FD portfolio allocation
    
    Parameters:
    - amount: Investment amount (Rs 1 Lakh - 10 Cr)
    - risk_profile: conservative | moderate | aggressive
    - tenure_months: 3, 6, 9, 12, 18, or 24 months
    - name: Your name for personalized report
    
    Returns: Personalized portfolio report with allocation table + AI recommendations
    """
    logger.info(f"Optimization request: amount={request.amount}, risk={request.risk_profile}, tenure={request.tenure_months}m")
    
    try:
        # Validate inputs
        if request.amount < 100000:
            raise ValueError("Minimum investment is Rs 1 Lakh")
        if request.amount > 100000000:
            raise ValueError("Maximum investment is Rs 10 Crore")
        if request.risk_profile not in ["conservative", "moderate", "aggressive"]:
            raise ValueError("Risk profile must be: conservative, moderate, or aggressive")
        if request.tenure_months not in [3, 6, 9, 12, 18, 24]:
            raise ValueError("Tenure must be: 3, 6, 9, 12, 18, or 24 months")
        
        # Run optimization
        user_input = {
            "amount": request.amount,
            "risk_profile": request.risk_profile,
            "tenure_months": request.tenure_months,
            "name": request.name,
            "tax_slab_pct": request.tax_slab_pct,
        }

        report = run_fd_optimizer(user_input)

        # Parse structured allocation from report text
        allocation = _parse_allocation_from_report(report, request.amount)
        annual_return = _parse_float(report, r'Expected Annual Return:\s*([\d.]+)%')
        total_interest = _parse_float(report, r'Total Interest Earned:\s*Rs([\d,]+\.?\d*)')
        total_maturity = _parse_float(report, r'Total Maturity Amount:\s*Rs([\d,]+\.?\d*)')
        pso_summary = {
            "total_investment":          request.amount,
            "total_interest_earned":     total_interest,
            "total_maturity_amount":     total_maturity,
            "expected_annual_return_pct":annual_return,
            "tenure_months":             request.tenure_months,
            "risk_profile":              request.risk_profile,
            "dicgc_fully_compliant":     all(a.get("dicgc_insured", False) for a in allocation) if allocation else False,
            "banks_used":                len(allocation),
        }

        # Run FD vs Alternatives Comparator
        comparison_rows, comparison_text, inflation_used = None, "", 5.5
        try:
            cmp = _compare_investment_alternatives(user_input, {"summary": pso_summary})
            comparison_rows = cmp.get("rows", [])
            comparison_text = cmp.get("table_text", "") + "\n" + cmp.get("recommendation", "")
            inflation_used  = cmp.get("inflation_used", 5.5)
        except Exception as cmp_err:
            logger.warning(f"Comparator skipped: {cmp_err}")

        # Get AI Agent recommendations
        banks_data = [
            {"name": "Bajaj Finance", "rate": 8.35},
            {"name": "Shriram Finance", "rate": 8.30},
            {"name": "Mahindra Finance", "rate": 8.20},
            {"name": "Suryoday SFB", "rate": 8.25},
            {"name": "Unity SFB", "rate": 8.15},
            {"name": "Utkarsh SFB", "rate": 8.10},
            {"name": "Shivalik SFB", "rate": 8.00},
            {"name": "Jana SFB", "rate": 7.90},
        ]
        
        # Agent 1: Bank Selection
        bank_rec = get_bank_recommendation(request.risk_profile, request.tenure_months, banks_data)
        
        # Agent 2: Rate Decision
        current_rate = 8.35 if request.risk_profile == "aggressive" else 8.25 if request.risk_profile == "moderate" else 8.15
        rate_decision = get_rate_decision(request.tenure_months, current_rate)
        
        logger.info("Optimization completed successfully with AI recommendations")
        
        return OptimizeResponse(
            success=True,
            report=report,
            bank_recommendation=bank_rec,
            rate_decision=rate_decision,
            allocation=allocation,
            summary=pso_summary,
            comparison_rows=comparison_rows,
            comparison_text=comparison_text,
            inflation_used=inflation_used,
            timestamp=datetime.now().isoformat(),
            request_params=user_input,
            error=None
        )
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return OptimizeResponse(
            success=False,
            report="",
            bank_recommendation="",
            rate_decision="",
            timestamp=datetime.now().isoformat(),
            request_params=request.model_dump(),
            error=f"Validation error: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return OptimizeResponse(
            success=False,
            report="",
            bank_recommendation="",
            rate_decision="",
            timestamp=datetime.now().isoformat(),
            request_params=request.model_dump(),
            error=f"Server error: {str(e)}"
        )


@app.get("/")
async def root():
    """API documentation redirect"""
    return {
        "message": "FD Portfolio Optimizer API v3.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "GET /health",
            "optimize": "POST /optimize"
        }
    }


# ── MAIN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  FD PORTFOLIO OPTIMIZER API v3.0.0")
    print("  Starting server on http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
