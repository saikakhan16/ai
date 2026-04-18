"""
FD Portfolio Optimizer API — Hybrid Version
REST API with both:
- Simple Pipeline (original)
- Hybrid Pipeline (with AI agent recommendations)

Choose endpoint based on your needs
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
from hybrid_main import run_hybrid_fd_optimizer

# ── LOGGING ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── FASTAPI APP ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="FD Portfolio Optimizer API — Hybrid",
    description="Optimizes FD allocation using PSO + AI Agent Recommendations",
    version="4.0.0"
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
    version: str
    pipeline_type: str  # "simple" or "hybrid"
    timestamp: str
    request_params: Dict[str, Any]
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    pipelines: list
    timestamp: str


# ── API ENDPOINTS ──────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="4.0.0",
        pipelines=["simple", "hybrid"],
        timestamp=datetime.now().isoformat()
    )


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_portfolio(request: OptimizeRequest) -> OptimizeResponse:
    """
    Main endpoint: Optimize FD portfolio (Simple Pipeline)
    
    Uses proven PSO algorithm with direct function calls.
    Fast, reliable, no rate limiting.
    
    Parameters:
    - amount: Investment amount (Rs 1 Lakh - 10 Cr)
    - risk_profile: conservative | moderate | aggressive
    - tenure_months: 3, 6, 9, 12, 18, or 24 months
    - name: Your name for personalized report
    
    Returns: Personalized portfolio report with allocation table
    """
    logger.info(f"Simple optimization: amount={request.amount}, risk={request.risk_profile}, tenure={request.tenure_months}m")
    
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
        
        logger.info("Simple optimization completed successfully")
        
        return OptimizeResponse(
            success=True,
            report=report,
            version="4.0.0",
            pipeline_type="simple",
            timestamp=datetime.now().isoformat(),
            request_params=user_input,
            error=None
        )
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return OptimizeResponse(
            success=False,
            report="",
            version="4.0.0",
            pipeline_type="simple",
            timestamp=datetime.now().isoformat(),
            request_params=request.dict(),
            error=f"Validation error: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return OptimizeResponse(
            success=False,
            report="",
            version="4.0.0",
            pipeline_type="simple",
            timestamp=datetime.now().isoformat(),
            request_params=request.dict(),
            error=f"Server error: {str(e)}"
        )


@app.post("/optimize-hybrid", response_model=OptimizeResponse)
async def optimize_portfolio_hybrid(request: OptimizeRequest) -> OptimizeResponse:
    """
    Hybrid endpoint: Optimize FD portfolio + AI Agent Recommendations
    
    Uses PSO algorithm PLUS:
    - Bank Recommendation Agent (which banks for your tenure)
    - Rate Decision Agent (book now or wait analysis)
    
    More intelligence, still fast and reliable.
    
    Parameters: Same as /optimize
    
    Returns: Enhanced report with:
    - PSO-optimized allocation
    - AI-driven bank recommendations
    - Market timing advice
    """
    logger.info(f"Hybrid optimization: amount={request.amount}, risk={request.risk_profile}, tenure={request.tenure_months}m")
    
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
        
        # Run hybrid optimization
        user_input = {
            "amount": request.amount,
            "risk_profile": request.risk_profile,
            "tenure_months": request.tenure_months,
            "name": request.name
        }
        
        report = run_hybrid_fd_optimizer(user_input)
        
        logger.info("Hybrid optimization completed successfully")
        
        return OptimizeResponse(
            success=True,
            report=report,
            version="4.0.0",
            pipeline_type="hybrid",
            timestamp=datetime.now().isoformat(),
            request_params=user_input,
            error=None
        )
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return OptimizeResponse(
            success=False,
            report="",
            version="4.0.0",
            pipeline_type="hybrid",
            timestamp=datetime.now().isoformat(),
            request_params=request.dict(),
            error=f"Validation error: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return OptimizeResponse(
            success=False,
            report="",
            version="4.0.0",
            pipeline_type="hybrid",
            timestamp=datetime.now().isoformat(),
            request_params=request.dict(),
            error=f"Server error: {str(e)}"
        )


@app.get("/")
async def root():
    """API documentation redirect"""
    return {
        "message": "FD Portfolio Optimizer API v4.0.0 — Hybrid",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "GET /health",
            "optimize_simple": "POST /optimize",
            "optimize_hybrid": "POST /optimize-hybrid"
        },
        "pipelines": {
            "simple": "Pure PSO algorithm (fast, reliable)",
            "hybrid": "PSO + 2 AI agents (smarter recommendations)"
        }
    }


# ── MAIN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("  FD PORTFOLIO OPTIMIZER API v4.0.0 — HYBRID")
    print("  Endpoints:")
    print("    Simple:  http://localhost:8000/optimize")
    print("    Hybrid:  http://localhost:8000/optimize-hybrid")
    print("    Docs:    http://localhost:8000/docs")
    print("="*70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
