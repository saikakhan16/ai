"""
FastAPI wrapper for the 6-Agent CrewAI system.
Exposes agent pipeline as REST API endpoints.
Connects to your existing FD Optimizer backend.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import uuid
import json
from datetime import datetime

app = FastAPI(
    title="FD Portfolio Optimizer — AI Agent API",
    description="6-Agent CrewAI System powered by Groq (Llama 3.3 70B)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (use Redis in production)
jobs: dict = {}


class OptimizeRequest(BaseModel):
    amount: float
    risk_profile: str = "moderate"   # conservative | moderate | aggressive
    tenure_months: int = 12
    name: Optional[str] = "Investor"


class JobStatus(BaseModel):
    job_id: str
    status: str   # pending | running | complete | failed
    result: Optional[dict] = None
    created_at: str
    completed_at: Optional[str] = None


def run_crew_sync(job_id: str, user_input: dict):
    """Runs the crew synchronously — called in background task"""
    try:
        jobs[job_id]["status"] = "running"
        from main import run_fd_crew
        result = run_fd_crew(user_input)
        jobs[job_id]["status"] = "complete"
        jobs[job_id]["result"] = result
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = {"error": str(e)}
        jobs[job_id]["completed_at"] = datetime.now().isoformat()


@app.post("/agent/optimize", response_model=JobStatus)
async def start_optimization(req: OptimizeRequest, background_tasks: BackgroundTasks):
    """
    Start the 6-agent optimization pipeline.
    Returns a job_id — poll /agent/status/{job_id} for results.
    Agents run async so the API doesn't timeout.
    """
    job_id = str(uuid.uuid4())[:8]
    user_input = {
        "amount": req.amount,
        "risk_profile": req.risk_profile,
        "tenure_months": req.tenure_months,
        "name": req.name
    }

    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "result": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "input": user_input
    }

    background_tasks.add_task(run_crew_sync, job_id, user_input)

    return JobStatus(**jobs[job_id])


@app.get("/agent/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Poll this endpoint to check if your optimization is complete."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**jobs[job_id])


@app.get("/agent/jobs")
async def list_jobs():
    """List all optimization jobs"""
    return {"jobs": list(jobs.values())}


@app.get("/agent/health")
async def health():
    """Check if agents are ready"""
    groq_key = __import__("os").getenv("GROQ_API_KEY")
    return {
        "status": "ready" if groq_key else "missing_groq_key",
        "agents": 6,
        "llm": "Groq Llama-3.3-70b-versatile",
        "framework": "CrewAI",
        "groq_key_set": bool(groq_key),
        "setup_url": "https://console.groq.com" if not groq_key else None
    }


@app.get("/")
async def root():
    return {
        "service": "FD Portfolio Optimizer — Agent API v2.0",
        "agents": {
            "1": "Orchestrator — coordinates all agents",
            "2": "Data Collector — live FD rates",
            "3": "Market Intelligence — RBI analysis",
            "4": "PSO Optimizer — swarm algorithm",
            "5": "Tax & Compliance — TDS + DICGC",
            "6": "User Advisor — plain language report"
        },
        "endpoints": {
            "POST /agent/optimize": "Start optimization pipeline",
            "GET /agent/status/{job_id}": "Check job status",
            "GET /agent/health": "Agent readiness check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
