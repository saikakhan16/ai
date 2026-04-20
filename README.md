# FD Portfolio Optimizer
## Hybrid AI System — PSO Algorithm + Groq LLM + 2 Live Agents

---

## Architecture

```
User Input (amount, risk, tenure)
           │
           ▼
┌──────────────────────────┐
│   Optimizer (Frontend)   │  ← Slider UI · risk profile · tenure
└────────────┬─────────────┘
             │ POST /optimize
             ▼
┌──────────────────────────┐
│   FastAPI  (api/index.py)│  ← Runs on localhost:8001
└────────────┬─────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌──────────┐    ┌─────────────────┐
│  PSO     │    │  Groq LLM       │
│Algorithm │    │  llama-3.1-8b   │
│60 part.  │    │  ~500 tokens    │
│200 iter. │    │  Advisory tips  │
└────┬─────┘    └──────┬──────────┘
     └────────┬─────────┘
              ▼
   { allocation[], summary{}, ladder[] }
              │
              ▼ sessionStorage
    ┌─────────────────────┐
    │  Browser Dashboard  │
    │                     │
    │  ┌───────────────┐  │
    │  │Bank Selection │  │  ← Agent β · 94% conf
    │  │    Agent      │  │    Real PSO banks + weights
    │  └───────────────┘  │
    │  ┌───────────────┐  │
    │  │Rate Decision  │  │  ← Agent ρ · 71% conf
    │  │    Agent      │  │    Tenure timing · watchlist
    │  └───────────────┘  │
    └─────────────────────┘
```

---

## Project Structure

```
AI/
├── api/
│   └── index.py          ← FastAPI server (port 8001) — main backend
├── api_vercel.py          ← Vercel serverless version
├── vercel.json            ← Deployment config
│
├── fd_agents/
│   ├── main.py            ← CLI entry point (PSO + Groq advisory)
│   ├── tasks.py           ← Task definitions
│   ├── requirements.txt
│   ├── .env               ← GROQ_API_KEY goes here
│   ├── agents/
│   │   ├── pso_optimizer.py   ← PSO algorithm (core engine)
│   │   ├── data_collector.py  ← Bank rate data + tools
│   │   └── user_advisor.py    ← Report generation
│   └── config/
│       └── llm.py         ← Groq LLM config
│
└── public/
    ├── Login.html         ← Landing / sign-in
    ├── Overview.html      ← Portfolio summary dashboard
    ├── Optimizer.html     ← Main input: amount · risk · tenure
    ├── Portfolio.html     ← FD ladder + allocation cards
    ├── Analytics.html     ← Bank table · maturity timeline
    ├── Agents.html        ← 2 live AI agents · reasoning cards
    ├── Renewal.html       ← Renewal & tax (Form 15G)
    └── assets/
        ├── app.css
        └── shell.js       ← Nav · sidebar · routing
```

---

## Quick Start

### Step 1 — Get FREE Groq API Key
```
1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. API Keys → Create Key
4. Copy the key (starts with gsk_)
```

### Step 2 — Setup
```bash
cd fd_agents
pip install -r requirements.txt

# Add your key to fd_agents/.env
echo "GROQ_API_KEY=gsk_your_key_here" > .env
```

### Step 3 — Start API server
```bash
cd api
uvicorn index:app --reload --port 8001
```

### Step 4 — Open frontend
```bash
# Serve public/ with any static server, e.g. Live Server in VS Code
# Open http://localhost:5500/public/Login.html
```

### Step 5 — Run CLI (optional, full report in terminal)
```bash
cd fd_agents
venv/Scripts/python main.py
```

---

## API Endpoints

```bash
# Health check
GET  http://localhost:8001/health

# Run optimization
POST http://localhost:8001/optimize
Content-Type: application/json

{
  "amount": 1000000,
  "risk_profile": "moderate",
  "tenure_months": 12,
  "name": "Rahul"
}
```

Response:
```json
{
  "success": true,
  "allocation": [
    { "bank_name": "Bajaj Finance", "weight_percent": 20.8, "interest_rate": 8.35 },
    ...
  ],
  "summary": {
    "total_investment": 1000000,
    "total_interest_earned": 82008,
    "total_maturity_amount": 1082008,
    "expected_annual_return_pct": 8.20
  },
  "ladder": [...],
  "pso": true,
  "timestamp": "2026-04-20T18:00:00"
}
```

---

## How the 2 Browser Agents Work

| Agent | Symbol | What it does |
|-------|--------|--------------|
| Bank Selection Agent | β | Ranks PSO output · recommends short/anchor rungs · checks DICGC caps · stress-tests −25 bps shock |
| Rate Decision Agent | ρ | Advises on timing (wait vs book) · flags low-rate banks · watchlist · long-term rung call |

Both read `optimizeResult` from `sessionStorage` and update their reasoning cards live after every optimization run. Timestamp shows exactly when the last run happened.

---

## 8 Partner Banks

| Bank | Type | Rating | 12mo Rate |
|------|------|--------|-----------|
| Bajaj Finance | NBFC | AAA | 8.35% |
| Shriram Finance | NBFC | AA+ | 8.30% |
| Suryoday SFB | Small Finance | AA | 8.25% |
| Mahindra Finance | NBFC | AA+ | 8.20% |
| Unity SFB | Small Finance | AA | 8.15% |
| Utkarsh SFB | Small Finance | AA | 8.10% |
| Shivalik SFB | Small Finance | A+ | 8.00% |
| Jana SFB | Small Finance | A+ | 7.90% |

---

## Cost Breakdown

| Resource | Cost |
|----------|------|
| Groq API (llama-3.1-8b-instant) | FREE |
| PSO Algorithm | FREE (pure Python) |
| FastAPI + Uvicorn | FREE |
| Vercel hosting | FREE tier |
| **Total** | **Rs 0** |

---

## Why Not Full CrewAI?

CrewAI builds ~29,000 token prompts per pipeline run. Groq free tier allows 6,000 tokens/minute — a single CrewAI run exceeds that limit 5x.

The hybrid approach uses ~500 tokens per run (98% reduction):
- PSO handles all math (no LLM needed)
- One direct Groq call generates personalized advisory tips
- Result: same quality, always within free tier limits

---

*Built with PSO Algorithm · Groq Llama 3.1 · FastAPI · Blostem Platform*
