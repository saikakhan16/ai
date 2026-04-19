"""
FD Portfolio Optimizer — Vercel Serverless Handler
Optimized for Vercel Python serverless environment
"""
import sys
import os

# Setup Python path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'fd_agents'))

# ──────────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# Try to import local modules - fallback to dummy if they fail
try:
    from simple_main import run_fd_optimizer
except Exception as e:
    logging.warning(f"Could not import simple_main: {e}")
    def run_fd_optimizer(*args, **kwargs):
        return {"allocation": {}, "returns": 0}

try:
    from agents.bank_selector_agent import get_bank_recommendation
except Exception as e:
    logging.warning(f"Could not import bank_selector_agent: {e}")
    def get_bank_recommendation(*args, **kwargs):
        return "<p>Bank recommendation unavailable</p>"

try:
    from agents.rate_decision_agent import get_rate_decision
except Exception as e:
    logging.warning(f"Could not import rate_decision_agent: {e}")
    def get_rate_decision(*args, **kwargs):
        return "<p>Rate decision unavailable</p>"

# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="FD Portfolio Optimizer API",
    description="Optimizes Fixed Deposit allocation across 8 banks",
    version="3.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# REQUEST/RESPONSE MODELS
# ──────────────────────────────────────────────────────────────────────────────

class OptimizeRequest(BaseModel):
    amount: float = Field(default=1000000, ge=100000, le=100000000)
    risk_profile: str = Field(default="moderate")
    tenure_months: int = Field(default=12, ge=3, le=24)
    name: str = Field(default="Investor")


class OptimizeResponse(BaseModel):
    success: bool
    report: str
    bank_recommendation: str = ""
    rate_decision: str = ""
    timestamp: str
    request_params: Dict[str, Any]
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str


# ──────────────────────────────────────────────────────────────────────────────
# API ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="3.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_portfolio(request: OptimizeRequest):
    """Main optimization endpoint"""
    try:
        # Get optimization result
        result = run_fd_optimizer(
            amount=request.amount,
            risk_profile=request.risk_profile,
            tenure_months=request.tenure_months,
            name=request.name
        )
        
        report = result.get("report", "Optimization completed")
        
        # Get AI agent recommendations
        banks_data = [
            {"name": "Bajaj Finance", "rate": 8.35, "type": "NBFC"},
            {"name": "Shriram Finance", "rate": 8.30, "type": "NBFC"},
            {"name": "Mahindra Finance", "rate": 8.20, "type": "NBFC"},
            {"name": "Suryoday SFB", "rate": 8.25, "type": "SFB"},
            {"name": "Unity SFB", "rate": 8.15, "type": "SFB"},
            {"name": "Utkarsh SFB", "rate": 8.10, "type": "SFB"},
            {"name": "Shivalik SFB", "rate": 8.00, "type": "SFB"},
            {"name": "Jana SFB", "rate": 7.90, "type": "SFB"},
        ]
        
        bank_rec = get_bank_recommendation(request.risk_profile, request.tenure_months, banks_data)
        rate_dec = get_rate_decision(request.tenure_months, 8.35)
        
        return OptimizeResponse(
            success=True,
            report=report,
            bank_recommendation=bank_rec,
            rate_decision=rate_dec,
            timestamp=datetime.now().isoformat(),
            request_params=request.dict()
        )
    
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        return OptimizeResponse(
            success=False,
            report="Optimization failed",
            timestamp=datetime.now().isoformat(),
            request_params=request.dict(),
            error=str(e)
        )


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "message": "FD Portfolio Optimizer API v3.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "optimize": "POST /optimize"
        }
    }


@app.get("/docs")
async def docs():
    """Redirect to Swagger docs"""
    return {"redirect": "/docs"}


# Export for Vercel
__all__ = ['app']
