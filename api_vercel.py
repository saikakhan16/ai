"""
FD Portfolio Optimizer — Vercel Serverless Handler (Root Level)
Optimized for Vercel Python serverless environment
"""
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
# HELPER FUNCTIONS
# ────────────────────────────────────────────────────────────────────

def get_bank_recommendation(risk_profile: str, tenure_months: int) -> str:
    """Simple bank recommendation based on risk profile"""
    if risk_profile == "conservative":
        return """
        <div style="background: #e8f5e9; padding: 15px; border-radius: 8px;">
            <h4>💚 Conservative Portfolio (Low Risk)</h4>
            <p><strong>Recommended Allocation:</strong></p>
            <ul>
                <li>Suryoday SFB: 40% @ 8.25%</li>
                <li>Unity SFB: 30% @ 8.15%</li>
                <li>Shivalik SFB: 20% @ 8.00%</li>
                <li>Jana SFB: 10% @ 7.90%</li>
            </ul>
        </div>
        """
    elif risk_profile == "aggressive":
        return """
        <div style="background: #ffebee; padding: 15px; border-radius: 8px;">
            <h4>🔥 Aggressive Portfolio (High Returns)</h4>
            <p><strong>Recommended Allocation:</strong></p>
            <ul>
                <li>Bajaj Finance: 40% @ 8.35%</li>
                <li>Shriram Finance: 35% @ 8.30%</li>
                <li>Mahindra Finance: 25% @ 8.20%</li>
            </ul>
        </div>
        """
    else:
        return """
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
            <h4>⚡ Moderate Portfolio (Balanced)</h4>
            <p><strong>Recommended Allocation:</strong></p>
            <ul>
                <li>Bajaj Finance: 25% @ 8.35%</li>
                <li>Suryoday SFB: 25% @ 8.25%</li>
                <li>Shriram Finance: 25% @ 8.30%</li>
                <li>Unity SFB: 25% @ 8.15%</li>
            </ul>
        </div>
        """


def get_rate_decision(tenure_months: int) -> str:
    """Rate decision based on tenure"""
    return """
    <div style="background: #fff3e0; padding: 15px; border-radius: 8px;">
        <h4>📊 Rate Decision</h4>
        <p><strong>RBI Policy Rate:</strong> 6.5% | <strong>Inflation:</strong> 4.2%</p>
        <p style="color: green; font-weight: bold;">✅ Book Now - Rates are Attractive</p>
    </div>
    """


# ────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/optimize")
async def optimize_portfolio(request: OptimizeRequest):
    """Portfolio optimization endpoint"""
    try:
        annual_return = request.amount * 0.0825  # 8.25% average
        
        report = f"""
        <h3>📋 Portfolio Report</h3>
        <p><strong>Investor:</strong> {request.name}</p>
        <p><strong>Amount:</strong> ₹{request.amount:,.0f}</p>
        <p><strong>Risk:</strong> {request.risk_profile.upper()}</p>
        <p><strong>Tenure:</strong> {request.tenure_months} months</p>
        <p><strong>Expected Return:</strong> ₹{annual_return:,.0f}/year</p>
        """
        
        return OptimizeResponse(
            success=True,
            report=report,
            bank_recommendation=get_bank_recommendation(request.risk_profile, request.tenure_months),
            rate_decision=get_rate_decision(request.tenure_months),
            timestamp=datetime.now().isoformat(),
            request_params=request.dict()
        )
    
    except Exception as e:
        return OptimizeResponse(
            success=False,
            report="Error in optimization",
            timestamp=datetime.now().isoformat(),
            request_params=request.dict(),
            error=str(e)
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FD Portfolio Optimizer API",
        "status": "running",
        "version": "3.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
