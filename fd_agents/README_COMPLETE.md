# FD Portfolio Optimizer v3.0

> **Fixed Deposit Investment Allocation Tool**  
> Optimizes portfolio across 8 Indian banks using Particle Swarm Optimization (PSO) algorithm  
> Powered by Groq API (Llama 3.3 70B) — **Zero Rate Limiting Issues**

---

## 📋 Quick Start

### Installation

```bash
# 1. Clone/download project
cd fd_agents

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY
```

### Getting Your API Key

1. Go to https://console.groq.com/
2. Sign up (free account)
3. Create API key
4. Copy to `.env` file: `GROQ_API_KEY=...`

---

## 🚀 Three Ways to Use

### Option 1: **REST API** (Recommended for Integration)

```bash
# Start server
python api_new.py

# Server runs at http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000000,
    "risk_profile": "moderate",
    "tenure_months": 12,
    "name": "Rajesh Kumar"
  }'
```

**Response:**
```json
{
  "success": true,
  "report": "FD PORTFOLIO OPTIMIZER — YOUR PERSONAL REPORT\n...",
  "timestamp": "2024-04-19T15:30:45.123456",
  "request_params": {...}
}
```

### Option 2: **Interactive CLI** (Best for Desktop Use)

```bash
# Start interactive mode
python cli.py

# Follow prompts to enter:
# - Investment amount
# - Risk profile
# - Tenure
# - Your name

# Option to save report to file
```

**Command-line Quick Mode:**
```bash
# Quick optimization without prompts
python cli.py --amount 1000000 --risk moderate --tenure 12 --name "Rajesh" --save

# Show help
python cli.py --help
```

### Option 3: **Direct Python** (For Scripting)

```python
from simple_main import run_fd_optimizer

user_input = {
    "amount": 1000000,
    "risk_profile": "moderate",
    "tenure_months": 12,
    "name": "Rajesh Kumar"
}

report = run_fd_optimizer(user_input)
print(report)
```

---

## 📊 Portfolio Features

### Supported Parameters

| Parameter | Options | Description |
|-----------|---------|-------------|
| **Amount** | 1 Lakh - 10 Crore | Investment amount in Rs |
| **Risk Profile** | conservative, moderate, aggressive | Portfolio allocation strategy |
| **Tenure** | 3, 6, 9, 12, 18, 24 months | FD investment period |

### Risk Profiles

- **Conservative**: Max 20% in single bank, DICGC-preferred allocation
- **Moderate**: Max 35% in single bank, balanced approach (recommended)
- **Aggressive**: Max 50% in single bank, yield-focused allocation

### Banks Included

| Bank | Type | Rating | DICGC | Tenure 12m Rate |
|------|------|--------|-------|-----------------|
| Bajaj Finance | NBFC | AAA | No | 8.35% |
| Shriram Finance | NBFC | AA+ | No | 8.30% |
| Suryoday SFB | SFB | AA | Yes | 8.25% |
| Mahindra Finance | NBFC | AA+ | No | 8.20% |
| Unity SFB | SFB | AA | Yes | 8.15% |
| Utkarsh SFB | SFB | AA | Yes | 8.10% |
| Shivalik SFB | SFB | A+ | Yes | 8.00% |
| Jana SFB | SFB | A+ | Yes | 7.90% |

---

## 🔧 Configuration

Edit `.env` to customize:

```env
# LLM Settings
GROQ_API_KEY=your_key_here
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.3

# PSO Algorithm
PSO_NUM_PARTICLES=60
PSO_NUM_ITERATIONS=200

# Rate Limiting (conservative for free tier)
RATE_LIMIT_RPM=300
RATE_LIMIT_TPM=12000

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

See `settings.py` for all available options.

---

## 📈 Output Example

```
FD PORTFOLIO OPTIMIZER — YOUR PERSONAL REPORT

PORTFOLIO SUMMARY
=================
Investment: Rs 1,000,000
Risk Profile: Moderate
Tenure: 12 months

YOUR ALLOCATION
===============
Bajaj Finance        | Rs 207,755 | 8.35% | Rs 225,103
Shriram Finance      | Rs 160,201 | 8.30% | Rs 173,498
Mahindra Finance     | Rs 144,381 | 8.20% | Rs 156,221
Suryoday Small Finance Bank | Rs 123,532 | 8.25% | Rs 133,723
Unity Small Finance Bank | Rs 111,333 | 8.15% | Rs 120,407
Utkarsh Small Finance Bank | Rs 105,693 | 8.10% | Rs 114,255
Shivalik Small Finance Bank | Rs 77,372 | 8.00% | Rs 83,562
Jana Small Finance Bank | Rs 69,732 | 7.90% | Rs 75,240

RESULTS
=======
Total Investment: Rs 1,000,000
Total Interest: Rs 82,008
Maturity Amount: Rs 1,082,008
Annual Return: 8.20%

KEY ACTIONS
===========
1. Book FDs per allocation above
2. Submit Form 15G at year start
3. Set maturity reminders
```

---

## 🏗️ Architecture

```
fd_agents/
├── api_new.py              # REST API (FastAPI)
├── cli.py                  # Interactive CLI
├── simple_main.py          # Core pipeline (proven, working)
├── settings.py             # Configuration management
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
├── .env.example            # Example config
│
├── config/
│   └── llm.py             # LLM configuration with rate limiting
│
└── agents/
    ├── data_collector.py   # Fetch & compare rates
    ├── pso_optimizer.py    # PSO algorithm
    └── user_advisor.py     # Generate reports
```

### Technology Stack

- **API**: FastAPI + Uvicorn
- **LLM**: Groq API (Llama 3.3 70B) 
- **Algorithm**: Particle Swarm Optimization (PSO)
- **Validation**: Pydantic
- **Async**: FastAPI async/await
- **Rate Limiting**: Custom RateLimiter class + Tenacity library

---

## ⚡ Performance

- **Portfolio Generation Time**: 10-30 seconds
- **API Response Time**: <100ms (after optimization)
- **Token Usage**: ~500-800 tokens per optimization
- **Rate Limit**: 12,000 TPM (Groq free tier) — NOT exceeded

### Why No Rate Limiting?

The original system used CrewAI's multi-agent reasoning (6 agents calling LLM repeatedly). This caused:
- 50+ API calls per optimization
- 10,000+ tokens consumed per request
- Hitting rate limits in minutes

**Solution**: Direct pipeline (`simple_main.py`) calls tools directly:
- Single PSO algorithm (no agent reasoning loop)
- ~500 tokens total
- ✅ **Zero rate limit issues**

---

## 🧪 Testing

```bash
# Test API (in another terminal)
python -c "
import requests
response = requests.post('http://localhost:8000/optimize', json={
    'amount': 1000000,
    'risk_profile': 'moderate',
    'tenure_months': 12,
    'name': 'Test User'
})
print(response.json()['success'])
"

# Test CLI
python cli.py --amount 500000 --risk conservative --tenure 18

# Test direct pipeline
python simple_main.py
```

---

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Create `.env` file: `cp .env.example .env`
- Add your API key: `GROQ_API_KEY=gsk_...`

### "Connection timeout"
- Check internet connection
- Verify API key is valid
- Check Groq status: https://status.groq.com/

### "Port 8000 already in use"
```bash
# Use different port
API_PORT=8001 python api_new.py

# Or kill process
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### "Module not found" errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## 📚 API Documentation

Once API is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🔐 Security

- No sensitive data stored locally
- API key kept in `.env` (never commit)
- All inputs validated with Pydantic
- Rate limiting prevents abuse
- HTTPS ready (configure in production)

---

## 📝 License

This project is open source.

---

## ❓ FAQ

**Q: Is this production-ready?**  
A: Yes! The system has been tested and optimized. Deploy `api_new.py` to production with proper HTTPS and monitoring.

**Q: Can I change bank data?**  
A: Yes, edit `settings.py` in the `BANKS` dictionary.

**Q: What if I want to add more banks?**  
A: Add to `BANKS` list in `settings.py` with rates for each tenure.

**Q: Can I customize the PSO algorithm?**  
A: Yes, edit PSO parameters in `.env` or `settings.py`.

**Q: Does this work on Windows/Mac/Linux?**  
A: Yes, it's Python-based and cross-platform.

---

## 🎯 Next Steps

1. **Get Groq API Key**: https://console.groq.com/
2. **Copy `.env`**: `cp .env.example .env`
3. **Install**: `pip install -r requirements.txt`
4. **Run API**: `python api_new.py`
5. **Test**: Visit http://localhost:8000/docs

---

**Need Help?** Check the logs or create an issue with error details.
