# FD Portfolio Optimizer
## Hybrid AI System — PSO Algorithm + Groq LLM + 2 Live Agents + FD vs Alternatives Comparator

---

## Architecture

```
User Input (amount, risk, tenure, tax_slab)
           │
           ▼
┌──────────────────────────┐
│   Optimizer (Frontend)   │  ← Slider UI · risk profile · tenure · tax bracket
└────────────┬─────────────┘
             │ POST /optimize
             ▼
┌──────────────────────────┐
│  FastAPI  (api_new.py)   │  ← Runs on localhost:8002
└────────────┬─────────────┘
             │
    ┌────────┴────────────────────┐
    ▼                             ▼
┌──────────┐              ┌──────────────────┐
│  PSO     │              │  Groq LLM        │
│Algorithm │              │  llama-3.1-8b    │
│60 part.  │              │  Bank Selection  │
│200 iter. │              │  Rate Decision   │
└────┬─────┘              └──────┬───────────┘
     │                           │
     └──────────┬────────────────┘
                ▼
   ┌─────────────────────────┐
   │  FD vs Alternatives     │  ← Comparator Agent
   │  Comparator Agent       │    FD · Debt MF · SGB · RD · PPF
   │  (Fisher equation,      │    Pre-tax / Post-tax / Real return
   │   CPI inflation, tax)   │
   └────────────┬────────────┘
                ▼
  { allocation[], summary{}, comparison_rows[], bank_recommendation, rate_decision }
                │
                ▼ sessionStorage
     ┌─────────────────────┐
     │  Browser Dashboard  │
     │  (public/ folder)   │
     │                     │
     │  Portfolio.html     │  ← Allocation donut · FD ladder · Comparator table
     │  Agents.html        │  ← Bank Selection Agent · Rate Decision Agent
     │  Analytics.html     │  ← Bank table · maturity timeline
     └─────────────────────┘
```

---

## Project Structure

```
AI/
├── api_new.py             ← Main FastAPI server (port 8002) — use this
├── api/
│   └── index.py           ← Legacy FastAPI (port 8001)
├── api_vercel.py          ← Vercel serverless version
├── vercel.json            ← Deployment config
│
├── fd_agents/
│   ├── api_new.py         ← FastAPI server (port 8002) ← START THIS
│   ├── simple_main.py     ← Direct pipeline (PSO + report, no CrewAI)
│   ├── main.py            ← CLI entry point
│   ├── tasks.py           ← Task definitions
│   ├── requirements.txt
│   ├── .env               ← GROQ_API_KEY goes here
│   └── agents/
│       ├── pso_optimizer.py     ← PSO algorithm (core engine)
│       ├── data_collector.py    ← Bank rate data + tools
│       ├── user_advisor.py      ← Report generation
│       ├── bank_selector_agent.py  ← Agent 1: Bank recommendation
│       ├── rate_decision_agent.py  ← Agent 2: Rate timing decision
│       └── comparator_agent.py     ← FD vs alternatives comparison
│
└── public/                ← Frontend (dark theme, Vercel deployed)
    ├── Login.html         ← Landing / sign-in
    ├── Overview.html      ← Portfolio summary dashboard
    ├── Optimizer.html     ← Input: amount · risk · tenure · tax bracket
    ├── Portfolio.html     ← Allocation · FD ladder · Comparator table
    ├── Analytics.html     ← Bank table · maturity timeline
    ├── Agents.html        ← 2 live AI agents · reasoning cards
    ├── Renewal.html       ← Renewal & tax (Form 15G)
    └── assets/
        ├── app.css        ← Dark theme styles
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
cd fd_agents
uvicorn api_new:app --host 0.0.0.0 --port 8002 --reload
```

### Step 4 — Open frontend
```bash
# Serve public/ with any static server, e.g. Live Server in VS Code
# Open http://localhost:5500/public/Login.html
```

### Step 5 — Run CLI (optional)
```bash
cd fd_agents
python simple_main.py
```

---

## API Endpoints

```bash
# Health check
GET  http://localhost:8002/health

# Run optimization
POST http://localhost:8002/optimize
Content-Type: application/json

{
  "amount": 1000000,
  "risk_profile": "moderate",
  "tenure_months": 12,
  "tax_slab_pct": 30,
  "name": "Investor"
}
```

Response:
```json
{
  "success": true,
  "allocation": [
    {
      "bank_name": "Bajaj Finance",
      "allocated_amount": 207755,
      "weight_percent": 20.78,
      "interest_rate": 8.35,
      "interest_earned": 17347,
      "maturity_amount": 225102,
      "dicgc_insured": true,
      "rating": "AAA"
    }
  ],
  "summary": {
    "total_investment": 1000000,
    "total_interest_earned": 82008,
    "total_maturity_amount": 1082008,
    "expected_annual_return_pct": 8.20,
    "banks_used": 8,
    "dicgc_fully_compliant": true
  },
  "comparison_rows": [
    { "instrument": "FD (Best)", "pre_tax_pct": 8.20, "post_tax_pct": 5.74, "real_return_pct": 0.23, "risk_score": 2, "liquidity_score": 7 },
    { "instrument": "SGB",       "pre_tax_pct": 10.55,"post_tax_pct": 9.80, "real_return_pct": 4.08, "risk_score": 3, "liquidity_score": 4 },
    { "instrument": "PPF",       "pre_tax_pct": 7.10, "post_tax_pct": 7.10, "real_return_pct": 1.52, "risk_score": 1, "liquidity_score": 3 }
  ],
  "comparison_text": "...",
  "inflation_used": 5.5,
  "bank_recommendation": "...",
  "rate_decision": "..."
}
```

---

## FD vs Alternatives Comparator

Compares Fixed Deposits against 4 other instruments using tax-adjusted and inflation-adjusted real returns:

| Instrument | Tax Treatment | Notes |
|---|---|---|
| FD (Best) | Taxed at income slab | DICGC insured up to ₹5L per bank |
| Debt Mutual Fund | Taxed at income slab (post Apr 2023) | No lock-in, high liquidity |
| SGB (Sovereign Gold Bond) | Gold appreciation tax-free at maturity; 2.5% coupon taxed at slab | 8-year maturity |
| Recurring Deposit | Taxed at income slab | Monthly commitment |
| PPF | EEE — fully exempt | 15-year lock-in |

**Real return formula:** `((1 + nominal) / (1 + inflation)) - 1` (Fisher equation)

CPI inflation fetched live from data.gov.in; falls back to **5.5%** if unavailable.

---

## AI Agents

| Agent | What it does |
|-------|--------------|
| Bank Selection Agent | Recommends banks based on risk profile, tenure, ratings |
| Rate Decision Agent | Advises book-now vs wait based on RBI policy cycle |
| Comparator Agent | Calculates post-tax real returns across 5 instruments |

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

CrewAI builds ~29,000 token prompts per pipeline run. Groq free tier allows 6,000 tokens/minute — a single CrewAI run exceeds that limit 5×.

The hybrid approach uses ~500 tokens per run (98% reduction):
- PSO handles all math (no LLM needed)
- Comparator agent runs pure Python (no LLM)
- One direct Groq call for bank & rate advisory
- Result: same quality, always within free tier limits

---

*Built with PSO Algorithm · Groq Llama 3.1 · FastAPI · Blostem Platform*
