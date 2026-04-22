"""
Standalone Railway entry point — no fd_agents import dependency.
All logic is self-contained here.
"""
import sys
import os

# Add fd_agents to path BEFORE any other imports
_root = os.path.dirname(os.path.abspath(__file__))
_fd = os.path.join(_root, "fd_agents")
if _fd not in sys.path:
    sys.path.insert(0, _fd)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import json, math, random, re, logging, traceback, urllib.request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FD Portfolio Optimizer API", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

# ── BANK DATA ─────────────────────────────────────────────────────────────────

BANKS = [
    {"id":"suryoday","name":"Suryoday Small Finance Bank","type":"Small Finance Bank","rating":"AA","dicgc":True,
     "rates":{"3":6.75,"6":7.25,"9":7.50,"12":8.25,"18":8.50,"24":8.35}},
    {"id":"unity","name":"Unity Small Finance Bank","type":"Small Finance Bank","rating":"AA","dicgc":True,
     "rates":{"3":6.50,"6":7.00,"9":7.35,"12":8.15,"18":8.40,"24":8.20}},
    {"id":"utkarsh","name":"Utkarsh Small Finance Bank","type":"Small Finance Bank","rating":"AA","dicgc":True,
     "rates":{"3":6.60,"6":7.10,"9":7.40,"12":8.10,"18":8.30,"24":8.15}},
    {"id":"shivalik","name":"Shivalik Small Finance Bank","type":"Small Finance Bank","rating":"A+","dicgc":True,
     "rates":{"3":6.40,"6":6.90,"9":7.25,"12":8.00,"18":8.20,"24":8.00}},
    {"id":"shriram","name":"Shriram Finance","type":"NBFC","rating":"AA+","dicgc":False,
     "rates":{"3":7.00,"6":7.50,"9":7.75,"12":8.30,"18":8.45,"24":8.50}},
    {"id":"bajaj","name":"Bajaj Finance","type":"NBFC","rating":"AAA","dicgc":False,
     "rates":{"3":7.15,"6":7.60,"9":7.80,"12":8.35,"18":8.50,"24":8.55}},
    {"id":"mahindra","name":"Mahindra Finance","type":"NBFC","rating":"AA+","dicgc":False,
     "rates":{"3":6.90,"6":7.40,"9":7.65,"12":8.20,"18":8.35,"24":8.40}},
    {"id":"jana","name":"Jana Small Finance Bank","type":"Small Finance Bank","rating":"A+","dicgc":True,
     "rates":{"3":6.30,"6":6.85,"9":7.20,"12":7.90,"18":8.10,"24":7.95}},
]

RATING_SCORES = {"AAA":0.010,"AA+":0.008,"AA":0.006,"A+":0.004,"A":0.002}
DICGC_LIMIT = 500_000

# ── PSO ───────────────────────────────────────────────────────────────────────

def run_pso(amount, risk, tenure):
    N = len(BANKS)
    def get_rate(b):
        t = str(tenure)
        if t in b["rates"]: return b["rates"][t]
        keys = [int(k) for k in b["rates"]]
        return b["rates"][str(min(keys, key=lambda x: abs(x-tenure)))]

    def normalize(pos):
        c = [max(0.001, p) for p in pos]
        s = sum(c); return [x/s for x in c]

    RISK_LIMITS = {"conservative":0.20,"moderate":0.35,"aggressive":0.50}
    W,C1,C2 = 0.729,1.494,1.494

    def fitness(pos):
        amounts = [w*amount for w in pos]
        ret = sum(amounts[i]*(get_rate(BANKS[i])/100)*(tenure/12) for i in range(N)) / amount
        pen_dicgc = sum(((a-DICGC_LIMIT)/amount)*2.0 for a in amounts if a>DICGC_LIMIT)
        mx = RISK_LIMITS.get(risk, 0.35)
        pen_conc = sum((w-mx)*1.5 for w in pos if w>mx)
        entropy = -sum(w*math.log(w+1e-10) for w in pos)
        div = (entropy/math.log(N))*0.02
        rat = sum(pos[i]*RATING_SCORES.get(BANKS[i].get("rating","A"),0.002) for i in range(N))
        return ret - pen_dicgc - pen_conc + div + rat

    particles = []
    for _ in range(60):
        pos = normalize([random.random() for _ in range(N)])
        vel = [(random.random()-0.5)*0.2 for _ in range(N)]
        particles.append({"pos":pos,"vel":vel,"bp":pos[:],"bs":fitness(pos)})

    gb = max(particles, key=lambda p: p["bs"])
    gp, gs = gb["bp"][:], gb["bs"]

    for it in range(200):
        w = W*(1-it/200*0.4)
        for p in particles:
            nv,np_ = [],[]
            for d in range(N):
                r1,r2 = random.random(),random.random()
                v = w*p["vel"][d]+C1*r1*(p["bp"][d]-p["pos"][d])+C2*r2*(gp[d]-p["pos"][d])
                v = max(-0.2,min(0.2,v))
                nv.append(v); np_.append(p["pos"][d]+v)
            p["vel"]=nv; p["pos"]=normalize(np_)
            sc=fitness(p["pos"])
            if sc>p["bs"]: p["bs"]=sc; p["bp"]=p["pos"][:]
            if sc>gs: gs=sc; gp=p["pos"][:]

    allocation,total_int = [],0
    for i,bank in enumerate(BANKS):
        w = gp[i]; a = w*amount
        r = get_rate(bank); intr = a*(r/100)*(tenure/12)
        total_int += intr
        allocation.append({
            "bank_name":bank["name"],"bank_id":bank["id"],
            "allocated_amount":round(a,2),"weight_percent":round(w*100,2),
            "interest_rate":r,"interest_earned":round(intr,2),
            "maturity_amount":round(a+intr,2),
            "dicgc_insured":a<=DICGC_LIMIT,"rating":bank.get("rating","A")
        })
    allocation.sort(key=lambda x: x["allocated_amount"], reverse=True)
    annual_return = (total_int/amount)*(12/tenure)*100
    return allocation, round(total_int,2), round(amount+total_int,2), round(annual_return,2)

# ── COMPARATOR ────────────────────────────────────────────────────────────────

def fetch_cpi():
    try:
        url = ("https://api.data.gov.in/resource/b49b6e1a-2a64-4c1b-a898-5c85b3fb99f7"
               "?format=json&limit=1")
        req = urllib.request.Request(url, headers={"User-Agent":"FDOptimizer/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            for rec in data.get("records",[]):
                for f in ["cpi_combined","value","cpi","index_number"]:
                    if f in rec:
                        v = float(rec[f])
                        if 2.0 <= v <= 15.0: return v
    except: pass
    return 5.5

def compare_alternatives(fd_rate, tax_slab, tenure_months, risk_profile):
    inflation = fetch_cpi()
    SGB_GOLD, SGB_COUPON = 8.05, 2.50

    def post_tax(pre, tax_type):
        if tax_type == "exempt": return pre
        if tax_type == "sgb": return SGB_GOLD + SGB_COUPON*(1-tax_slab/100)
        return pre*(1-tax_slab/100)

    def real(pt): return ((1+pt/100)/(1+inflation/100)-1)*100

    instruments = [
        ("FD (Best)", fd_rate, "slab", 2, 7, "DICGC insured up to Rs5L"),
        ("Debt Mutual Fund", 7.2, "slab", 4, 9, "No lock-in; taxed at slab"),
        ("SGB", SGB_GOLD+SGB_COUPON, "sgb", 3, 4, "Gold gain tax-free at maturity"),
        ("Recurring Deposit", 7.0, "slab", 2, 6, "Monthly commitment"),
        ("PPF", 7.1, "exempt", 1, 3, "EEE; 15yr lock-in"),
    ]
    rows = []
    for name,pre,tt,risk,liq,notes in instruments:
        pt = post_tax(pre,tt); rl = real(pt)
        rows.append({"instrument":name,"pre_tax_pct":round(pre,2),"post_tax_pct":round(pt,2),
                     "real_return_pct":round(rl,2),"risk_score":risk,"liquidity_score":liq,"notes":notes})
    return rows, inflation

# ── REPORT ───────────────────────────────────────────────────────────────────

def generate_report(allocation, total_int, total_mat, annual_ret, name, amount, tenure):
    lines = [
        f"FD PORTFOLIO OPTIMIZER — REPORT FOR {name.upper()}",
        "="*60,
        f"Total Investment: Rs{amount:,.0f}",
        f"Total Interest Earned: Rs{total_int:,.0f}",
        f"Total Maturity Amount: Rs{total_mat:,.0f}",
        f"Expected Annual Return: {annual_ret:.2f}%",
        f"Tenure: {tenure} months",
        "",
        "Bank Name | Amount | Rate | Maturity",
        "-"*50,
    ]
    for a in allocation:
        if a["weight_percent"] > 1:
            lines.append(f"{a['bank_name']:20} | Rs{a['allocated_amount']:,.0f} | {a['interest_rate']:.2f}% | Rs{a['maturity_amount']:,.0f}")
    lines += ["","KEY ACTIONS:","1. Book FDs per the allocation above",
              "2. Submit Form 15G if income below Rs5L","3. Set maturity reminders"]
    return "\n".join(lines)

# ── BANK RECOMMENDATION ───────────────────────────────────────────────────────

BANK_REC = {
    "conservative": "BANK SELECTION (Conservative): Prioritise SFBs — Suryoday SFB (8.25%), Utkarsh SFB (8.10%), Jana SFB (7.90%). All DICGC insured. Split 50/35/15 across these three banks.",
    "moderate": "BANK SELECTION (Moderate): Mix NBFCs + SFBs — Bajaj Finance (8.35%), Shriram Finance (8.30%), Suryoday SFB (8.25%). Split 35/25/20/20 across top four banks.",
    "aggressive": "BANK SELECTION (Aggressive): Top-rated NBFCs only — Bajaj Finance (8.35%), Shriram Finance (8.30%), Mahindra Finance (8.20%). Split 40/35/25. Note: NBFCs not DICGC insured.",
}

RATE_DEC = ("RATE DECISION: BOOK NOW — FD rates at cycle peak (8.35%). RBI likely to cut rates from June 2026. "
            "Lock in today to capture maximum returns. Each 0.25% RBI cut reduces FD rates by ~0.20-0.25%.")

# ── MODELS ───────────────────────────────────────────────────────────────────

class OptimizeRequest(BaseModel):
    amount: float = Field(default=1000000, ge=100000, le=100000000)
    risk_profile: str = Field(default="moderate")
    tenure_months: int = Field(default=12, ge=3, le=24)
    name: str = Field(default="Investor")
    tax_slab_pct: int = Field(default=30)

# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "3.0.0", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {"message": "FD Portfolio Optimizer API v3.0.0", "health": "/health", "optimize": "POST /optimize"}

@app.post("/optimize")
async def optimize(request: OptimizeRequest):
    logger.info(f"Request: amount={request.amount}, risk={request.risk_profile}, tenure={request.tenure_months}")
    try:
        if request.risk_profile not in ["conservative","moderate","aggressive"]:
            return {"success":False,"error":"risk_profile must be conservative, moderate, or aggressive"}
        if request.tenure_months not in [3,6,9,12,18,24]:
            return {"success":False,"error":"tenure_months must be 3, 6, 9, 12, 18, or 24"}

        allocation, total_int, total_mat, annual_ret = run_pso(
            request.amount, request.risk_profile, request.tenure_months)

        report = generate_report(allocation, total_int, total_mat, annual_ret,
                                  request.name, request.amount, request.tenure_months)

        summary = {
            "total_investment": request.amount,
            "total_interest_earned": total_int,
            "total_maturity_amount": total_mat,
            "expected_annual_return_pct": annual_ret,
            "tenure_months": request.tenure_months,
            "risk_profile": request.risk_profile,
            "dicgc_fully_compliant": all(a["dicgc_insured"] for a in allocation),
            "banks_used": sum(1 for a in allocation if a["weight_percent"] > 2),
        }

        comparison_rows, inflation_used = [], 5.5
        try:
            comparison_rows, inflation_used = compare_alternatives(
                annual_ret, request.tax_slab_pct, request.tenure_months, request.risk_profile)
        except Exception as e:
            logger.warning(f"Comparator skipped: {e}")

        return {
            "success": True,
            "report": report,
            "allocation": allocation,
            "summary": summary,
            "comparison_rows": comparison_rows,
            "comparison_text": "",
            "inflation_used": inflation_used,
            "bank_recommendation": BANK_REC.get(request.risk_profile, BANK_REC["moderate"]),
            "rate_decision": RATE_DEC,
            "timestamp": datetime.now().isoformat(),
            "request_params": request.model_dump(),
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        return {"success":False,"error":str(e),"timestamp":datetime.now().isoformat(),
                "request_params":request.model_dump()}
