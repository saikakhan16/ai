"""
Agent 4: PSO Optimizer Agent
Runs the Particle Swarm Optimization algorithm as a CrewAI tool.
This is the mathematical core — allocates funds across banks to maximize returns.
"""

import json
import math
import random


# ── PSO ALGORITHM AS A TOOL ───────────────────────────────────────────────────

def _run_pso_optimization(params: str) -> str:
    """Internal PSO implementation (unwrapped for direct use)"""
    try:
        p = json.loads(params) if isinstance(params, str) else params
    except Exception:
        p = {"total_amount": 1000000, "risk_profile": "moderate", "tenure_months": 12}

    amount = float(p.get("total_amount", 1000000))
    risk = p.get("risk_profile", "moderate")
    tenure = int(p.get("tenure_months", 12))

    # Default bank data if not passed
    banks = p.get("banks", [
        {"id":"suryoday","name":"Suryoday SFB","rating":"AA","dicgc":True,
         "rates":{"3":6.75,"6":7.25,"9":7.50,"12":8.25,"18":8.50,"24":8.35}},
        {"id":"unity","name":"Unity SFB","rating":"AA","dicgc":True,
         "rates":{"3":6.50,"6":7.00,"9":7.35,"12":8.15,"18":8.40,"24":8.20}},
        {"id":"utkarsh","name":"Utkarsh SFB","rating":"AA","dicgc":True,
         "rates":{"3":6.60,"6":7.10,"9":7.40,"12":8.10,"18":8.30,"24":8.15}},
        {"id":"shivalik","name":"Shivalik SFB","rating":"A+","dicgc":True,
         "rates":{"3":6.40,"6":6.90,"9":7.25,"12":8.00,"18":8.20,"24":8.00}},
        {"id":"shriram","name":"Shriram Finance","rating":"AA+","dicgc":False,
         "rates":{"3":7.00,"6":7.50,"9":7.75,"12":8.30,"18":8.45,"24":8.50}},
        {"id":"bajaj","name":"Bajaj Finance","rating":"AAA","dicgc":False,
         "rates":{"3":7.15,"6":7.60,"9":7.80,"12":8.35,"18":8.50,"24":8.55}},
        {"id":"mahindra","name":"Mahindra Finance","rating":"AA+","dicgc":False,
         "rates":{"3":6.90,"6":7.40,"9":7.65,"12":8.20,"18":8.35,"24":8.40}},
        {"id":"jana","name":"Jana SFB","rating":"A+","dicgc":True,
         "rates":{"3":6.30,"6":6.85,"9":7.20,"12":7.90,"18":8.10,"24":7.95}},
    ])

    N = len(banks)
    DICGC_LIMIT = 500000
    RISK_LIMITS = {"conservative": 0.20, "moderate": 0.35, "aggressive": 0.50}
    W, C1, C2 = 0.729, 1.494, 1.494
    N_PARTICLES, MAX_ITER = 60, 200

    def get_rate(bank):
        t = str(tenure)
        if t in bank["rates"]: return bank["rates"][t]
        keys = [int(k) for k in bank["rates"]]
        closest = min(keys, key=lambda x: abs(x - tenure))
        return bank["rates"][str(closest)]

    def normalize(pos):
        clipped = [max(0.001, p) for p in pos]
        total = sum(clipped)
        return [c / total for c in clipped]

    rating_scores = {"AAA": 0.010, "AA+": 0.008, "AA": 0.006, "A+": 0.004, "A": 0.002}

    def fitness(pos):
        amounts = [w * amount for w in pos]
        total_return = sum(amounts[i] * (get_rate(banks[i]) / 100) * (tenure / 12) for i in range(N))
        norm_return = total_return / amount
        dicgc_penalty = sum(((a - DICGC_LIMIT) / amount) * 2.0 for a in amounts if a > DICGC_LIMIT)
        max_conc = RISK_LIMITS.get(risk, 0.35)
        conc_penalty = sum((w - max_conc) * 1.5 for w in pos if w > max_conc)
        entropy = -sum(w * math.log(w + 1e-10) for w in pos)
        div_bonus = (entropy / math.log(N)) * 0.02
        rating_bonus = sum(pos[i] * rating_scores.get(banks[i].get("rating", "A"), 0.002) for i in range(N))
        return norm_return - dicgc_penalty - conc_penalty + div_bonus + rating_bonus

    # Initialize swarm
    particles = []
    for _ in range(N_PARTICLES):
        pos = normalize([random.random() for _ in range(N)])
        vel = [(random.random() - 0.5) * 0.2 for _ in range(N)]
        score = fitness(pos)
        particles.append({"pos": pos, "vel": vel, "best_pos": pos[:], "best_score": score})

    g_best = max(particles, key=lambda p: p["best_score"])
    g_best_pos = g_best["best_pos"][:]
    g_best_score = g_best["best_score"]

    # Run PSO
    convergence = []
    for iteration in range(MAX_ITER):
        w = W * (1 - iteration / MAX_ITER * 0.4)
        for p in particles:
            new_vel, new_pos = [], []
            for d in range(N):
                r1, r2 = random.random(), random.random()
                v = w * p["vel"][d] + C1*r1*(p["best_pos"][d]-p["pos"][d]) + C2*r2*(g_best_pos[d]-p["pos"][d])
                v = max(-0.2, min(0.2, v))
                new_vel.append(v)
                new_pos.append(p["pos"][d] + v)
            p["vel"] = new_vel
            p["pos"] = normalize(new_pos)
            score = fitness(p["pos"])
            if score > p["best_score"]:
                p["best_score"] = score
                p["best_pos"] = p["pos"][:]
            if score > g_best_score:
                g_best_score = score
                g_best_pos = p["pos"][:]
        convergence.append(round(g_best_score, 6))

    # Build result
    total_interest = 0
    allocation = []
    for i, bank in enumerate(banks):
        w = g_best_pos[i]
        alloc_amount = w * amount
        rate = get_rate(bank)
        interest = alloc_amount * (rate / 100) * (tenure / 12)
        total_interest += interest
        allocation.append({
            "bank_name": bank["name"],
            "bank_id": bank["id"],
            "allocated_amount": round(alloc_amount, 2),
            "weight_percent": round(w * 100, 2),
            "interest_rate": rate,
            "interest_earned": round(interest, 2),
            "maturity_amount": round(alloc_amount + interest, 2),
            "dicgc_insured": alloc_amount <= DICGC_LIMIT,
            "rating": bank.get("rating", "A")
        })

    allocation.sort(key=lambda x: x["allocated_amount"], reverse=True)
    annual_return = (total_interest / amount) * (12 / tenure) * 100

    # Build ladder
    ladder = []
    for alloc in allocation[:4]:
        bank = next((b for b in banks if b["id"] == alloc["bank_id"]), None)
        if not bank: continue
        for t, split in [(3, 0.20), (6, 0.25), (9, 0.25), (12, 0.30)]:
            a = alloc["allocated_amount"] * split
            r = bank["rates"].get(str(t), bank["rates"].get("12", 7.0))
            intr = a * (r / 100) * (t / 12)
            ladder.append({"bank": alloc["bank_name"], "tenure_months": t,
                           "amount": round(a, 2), "rate": r,
                           "maturity_amount": round(a + intr, 2)})

    result = {
        "allocation": allocation,
        "summary": {
            "total_investment": amount,
            "total_interest_earned": round(total_interest, 2),
            "total_maturity_amount": round(amount + total_interest, 2),
            "expected_annual_return_pct": round(annual_return, 2),
            "tenure_months": tenure,
            "risk_profile": risk,
            "dicgc_fully_compliant": all(a["dicgc_insured"] for a in allocation),
            "banks_used": sum(1 for a in allocation if a["weight_percent"] > 2),
            "pso_fitness_score": round(g_best_score, 4),
            "iterations": MAX_ITER,
            "particles": N_PARTICLES
        },
        "ladder_strategy": sorted(ladder, key=lambda x: x["tenure_months"])
    }
    return json.dumps(result, indent=2)


