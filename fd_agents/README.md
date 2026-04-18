# 🐝 FD Portfolio Optimizer — 6-Agent AI System
## Powered by Groq (Free) + CrewAI + Particle Swarm Optimization

---

## 🏗️ Agent Architecture

```
User Request (amount, risk, tenure)
           │
           ▼
┌─────────────────────────┐
│   Agent 1: Orchestrator  │  ← Coordinates all agents, delegates tasks
│   Role: Senior FD Mgr   │
└────────────┬────────────┘
             │ assigns tasks
    ┌────────┴────────┐
    ▼                 ▼
┌──────────┐    ┌──────────────┐
│ Agent 2  │    │   Agent 3    │
│ Data     │    │ Market Intel │  ← Run in parallel
│Collector │    │ RBI Analysis │
└────┬─────┘    └──────┬───────┘
     └────────┬─────────┘
              ▼
     ┌──────────────────┐
     │    Agent 4       │
     │  PSO Optimizer   │  ← Swarm algo (60 particles × 200 iter)
     │  (Core Engine)   │
     └────────┬─────────┘
              ▼
     ┌──────────────────┐
     │    Agent 5       │
     │ Tax & Compliance │  ← TDS, DICGC, Form 15G/15H
     └────────┬─────────┘
              ▼
     ┌──────────────────┐
     │    Agent 6       │
     │  User Advisor    │  ← Plain language final report
     └────────┬─────────┘
              ▼
     📊 Complete Portfolio Report
```

---

## 📁 Project Structure

```
fd_agents/
├── main.py              ← Entry point, crew assembly
├── api.py               ← FastAPI REST wrapper
├── tasks.py             ← All 5 CrewAI task definitions
├── requirements.txt
├── .env.example
├── agents/
│   ├── orchestrator.py  ← Agent 1: Boss, delegates
│   ├── data_collector.py← Agent 2: Live FD rates
│   ├── market_intel.py  ← Agent 3: RBI/macro analysis
│   ├── pso_optimizer.py ← Agent 4: Swarm algorithm
│   ├── tax_compliance.py← Agent 5: TDS + DICGC
│   └── user_advisor.py  ← Agent 6: Final report
└── config/
    └── llm.py           ← Groq LLM configuration
```

---

## ⚡ Quick Start

### Step 1 — Get FREE Groq API Key
```
1. Go to https://console.groq.com
2. Sign up (free, no credit card needed)
3. Click "API Keys" → "Create API Key"
4. Copy the key
```

### Step 2 — Setup
```bash
# Clone / download the project
cd fd_agents

# Install dependencies
pip install -r requirements.txt

# Set your Groq key
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY
```

### Step 3 — Run (CLI mode)
```bash
export GROQ_API_KEY="your_key_here"
python main.py
```

### Step 4 — Run (API mode)
```bash
python api.py
# API runs at http://localhost:8001
# Docs at http://localhost:8001/docs
```

---

## 🔌 API Usage

### Start Optimization
```bash
curl -X POST http://localhost:8001/agent/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000000,
    "risk_profile": "moderate",
    "tenure_months": 12,
    "name": "Rahul"
  }'
```
Returns: `{ "job_id": "a1b2c3d4", "status": "pending" }`

### Check Status
```bash
curl http://localhost:8001/agent/status/a1b2c3d4
```
Returns: `{ "status": "complete", "result": { "report": "..." } }`

### Health Check
```bash
curl http://localhost:8001/agent/health
```

---

## 🤖 Agent Details

| # | Agent | LLM | Tools | Purpose |
|---|-------|-----|-------|---------|
| 1 | Orchestrator | Llama 3.3 70B | delegation | Coordinates all agents |
| 2 | Data Collector | Llama 3.3 70B | FetchLiveFDRates, CompareBankRates | Gets live rates |
| 3 | Market Intel | Llama 3.3 70B | GetRBIRateAnalysis, GetMacroIndicators | Rate timing signal |
| 4 | PSO Optimizer | Llama 3.3 70B | RunPSOOptimization, BuildFDLadder | Core algorithm |
| 5 | Tax Compliance | Llama 3.3 70B | CalculateTDSAndTax, VerifyDICGCCompliance | Tax advisory |
| 6 | User Advisor | Llama 3.3 70B | GeneratePortfolioReport, SimplifyForUser | Final report |

---

## 💰 Cost Breakdown

| Resource | Cost |
|----------|------|
| Groq API | **FREE** (14,400 req/day) |
| CrewAI framework | **FREE** (open source) |
| LLM (Llama 3.3 70B) | **FREE** on Groq |
| Hosting (Vercel) | **FREE** tier |
| **Total** | **₹0** |

---

## 🔮 Production Upgrades

1. **Swap `/tmp` SQLite → Supabase** (free Postgres)
2. **Add real web scraper** in data_collector.py using BeautifulSoup
3. **Add Serper API** for Agent 3 to search live RBI news
4. **Add WhatsApp notifs** via Twilio when FD matures
5. **Add memory persistence** via Redis instead of in-memory dict

---

*Built with CrewAI · Groq · FastAPI · PSO Algorithm · Blostem Platform*
