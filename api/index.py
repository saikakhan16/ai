"""
FD Portfolio Optimizer — Vercel Serverless Handler (Minimal & Robust)
"""
import sys, os, json

# Import real PSO algorithm
try:
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(_root, 'fd_agents'))
    from agents.pso_optimizer import _run_pso_optimization
    PSO_AVAILABLE = True
except Exception:
    PSO_AVAILABLE = False

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# ────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="FD Portfolio Optimizer API",
    description="Optimizes Fixed Deposit allocation across 8 banks",
    version="3.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────────────────────────
# MODELS
# ────────────────────────────────────────────────────────────────────

class OptimizeRequest(BaseModel):
    amount: float = 1000000
    risk_profile: str = "moderate"
    tenure_months: int = 12
    name: str = "Investor"


class OptimizeResponse(BaseModel):
    success: bool
    report: str
    bank_recommendation: str = ""
    rate_decision: str = ""
    timestamp: str
    request_params: Dict[str, Any]
    error: Optional[str] = None


# ────────────────────────────────────────────────────────────────────
# DUMMY DATA & FUNCTIONS
# ────────────────────────────────────────────────────────────────────

BANKS = [
    {"name": "Bajaj Finance", "rate": 8.35, "type": "NBFC"},
    {"name": "Shriram Finance", "rate": 8.30, "type": "NBFC"},
    {"name": "Mahindra Finance", "rate": 8.20, "type": "NBFC"},
    {"name": "Suryoday SFB", "rate": 8.25, "type": "SFB"},
    {"name": "Unity SFB", "rate": 8.15, "type": "SFB"},
    {"name": "Utkarsh SFB", "rate": 8.10, "type": "SFB"},
    {"name": "Shivalik SFB", "rate": 8.00, "type": "SFB"},
    {"name": "Jana SFB", "rate": 7.90, "type": "SFB"},
]


def get_bank_recommendation(risk_profile: str, tenure_months: int) -> str:
    """Simple bank recommendation based on risk profile"""
    if risk_profile == "conservative":
        return """
        <div style="background: #e8f5e9; padding: 15px; border-radius: 8px;">
            <h4>💚 Conservative Portfolio (Low Risk)</h4>
            <p><strong>Recommended Allocation:</strong></p>
            <ul>
                <li>Suryoday SFB: 40% (₹400,000) @ 8.25%</li>
                <li>Unity SFB: 30% (₹300,000) @ 8.15%</li>
                <li>Shivalik SFB: 20% (₹200,000) @ 8.00%</li>
                <li>Jana SFB: 10% (₹100,000) @ 7.90%</li>
            </ul>
            <p><strong>Expected Returns:</strong> ₹99,000 per year</p>
        </div>
        """
    elif risk_profile == "aggressive":
        return """
        <div style="background: #ffebee; padding: 15px; border-radius: 8px;">
            <h4>🔥 Aggressive Portfolio (High Returns)</h4>
            <p><strong>Recommended Allocation:</strong></p>
            <ul>
                <li>Bajaj Finance: 40% (₹400,000) @ 8.35%</li>
                <li>Shriram Finance: 35% (₹350,000) @ 8.30%</li>
                <li>Mahindra Finance: 25% (₹250,000) @ 8.20%</li>
            </ul>
            <p><strong>Expected Returns:</strong> ₹125,500 per year</p>
        </div>
        """
    else:  # moderate
        return """
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
            <h4>⚡ Moderate Portfolio (Balanced)</h4>
            <p><strong>Recommended Allocation:</strong></p>
            <ul>
                <li>Bajaj Finance: 25% (₹250,000) @ 8.35%</li>
                <li>Suryoday SFB: 25% (₹250,000) @ 8.25%</li>
                <li>Shriram Finance: 25% (₹250,000) @ 8.30%</li>
                <li>Unity SFB: 25% (₹250,000) @ 8.15%</li>
            </ul>
            <p><strong>Expected Returns:</strong> ₹101,000 per year</p>
        </div>
        """


def get_rate_decision(tenure_months: int) -> str:
    """Simple rate decision"""
    return """
    <div style="background: #fff3e0; padding: 15px; border-radius: 8px;">
        <h4>📊 Rate Decision Analysis</h4>
        <p><strong>Current RBI Rate:</strong> 6.5% | <strong>Inflation:</strong> 4.2%</p>
        <p><strong>Recommendation:</strong> <span style="color: green; font-weight: bold;">✅ BOOK NOW</span></p>
        <p>Current FD rates are attractive. Rates may decline if RBI cuts policy rate.</p>
    </div>
    """


# ────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/optimize")
async def optimize_portfolio(request: OptimizeRequest):
    """Portfolio optimization — runs real PSO algorithm (60 particles × 200 iterations)"""
    try:
        if PSO_AVAILABLE:
            params = json.dumps({
                "total_amount": request.amount,
                "risk_profile": request.risk_profile,
                "tenure_months": request.tenure_months
            })
            pso_data = json.loads(_run_pso_optimization(params))
            allocation = [a for a in pso_data["allocation"] if a["weight_percent"] > 3]
            return {
                "success": True,
                "allocation": allocation,
                "summary": pso_data["summary"],
                "ladder": pso_data.get("ladder_strategy", []),
                "pso": True,
                "timestamp": datetime.now().isoformat(),
                "request_params": request.dict()
            }

        # Fallback (no PSO)
        fallback = {
            "conservative": [
                {"bank_name":"Suryoday SFB","rating":"AA+","weight_percent":40,"interest_rate":8.25,"dicgc_insured":True},
                {"bank_name":"Unity SFB","rating":"AA+","weight_percent":30,"interest_rate":8.15,"dicgc_insured":True},
                {"bank_name":"Shivalik SFB","rating":"AA","weight_percent":20,"interest_rate":8.00,"dicgc_insured":True},
                {"bank_name":"Jana SFB","rating":"AA","weight_percent":10,"interest_rate":7.90,"dicgc_insured":True},
            ],
            "moderate": [
                {"bank_name":"Bajaj Finance","rating":"AAA","weight_percent":25,"interest_rate":8.35,"dicgc_insured":False},
                {"bank_name":"Suryoday SFB","rating":"AA+","weight_percent":25,"interest_rate":8.25,"dicgc_insured":True},
                {"bank_name":"Shriram Finance","rating":"AA+","weight_percent":25,"interest_rate":8.30,"dicgc_insured":False},
                {"bank_name":"Unity SFB","rating":"AA+","weight_percent":25,"interest_rate":8.15,"dicgc_insured":True},
            ],
            "aggressive": [
                {"bank_name":"Bajaj Finance","rating":"AAA","weight_percent":40,"interest_rate":8.35,"dicgc_insured":False},
                {"bank_name":"Shriram Finance","rating":"AA+","weight_percent":35,"interest_rate":8.30,"dicgc_insured":False},
                {"bank_name":"Mahindra Finance","rating":"AA+","weight_percent":25,"interest_rate":8.20,"dicgc_insured":False},
            ],
        }
        alloc = fallback.get(request.risk_profile, fallback["moderate"])
        blended = sum(a["weight_percent"] * a["interest_rate"] / 100 for a in alloc)
        gross = request.amount * blended / 100
        return {
            "success": True,
            "allocation": alloc,
            "summary": {
                "total_investment": request.amount,
                "total_interest_earned": round(gross, 2),
                "total_maturity_amount": round(request.amount + gross, 2),
                "expected_annual_return_pct": round(blended, 2),
                "tenure_months": request.tenure_months,
                "risk_profile": request.risk_profile,
            },
            "ladder": [],
            "pso": False,
            "timestamp": datetime.now().isoformat(),
            "request_params": request.dict()
        }

    except Exception as e:
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat(), "request_params": request.dict()}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FD Portfolio Optimizer API v3.0.0",
        "status": "ready",
        "endpoints": {
            "health": "GET /health",
            "optimize": "POST /optimize"
        }
    }

