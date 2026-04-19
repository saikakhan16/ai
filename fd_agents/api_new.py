"""
FD Portfolio Optimizer — REST API
Lightweight FastAPI using the proven simple_main.py pipeline
No CrewAI overhead — minimal token usage
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import logging
from datetime import datetime
import traceback

from simple_main import run_fd_optimizer
from agents.bank_selector_agent import get_bank_recommendation
from agents.rate_decision_agent import get_rate_decision

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

    class Config:
        example = {
            "amount": 1500000,
            "risk_profile": "moderate",
            "tenure_months": 12,
            "name": "Rajesh Kumar"
        }


class OptimizeResponse(BaseModel):
    """API response with optimization result"""
    success: bool
    report: str
    bank_recommendation: str = ""
    rate_decision: str = ""
    timestamp: str
    request_params: Dict[str, Any]
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str


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
            "name": request.name
        }
        
        report = run_fd_optimizer(user_input)
        
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
            request_params=request.dict(),
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
            request_params=request.dict(),
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
