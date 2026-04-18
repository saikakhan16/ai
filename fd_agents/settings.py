"""
FD Portfolio Optimizer Configuration
Central config for LLM, banks, PSO parameters, limits, etc.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── ENVIRONMENT ────────────────────────────────────────────────────────────────

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ── LLM CONFIGURATION (Groq) ──────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))

# Rate limiting for Groq API
RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "300"))  # Requests per minute
RATE_LIMIT_TPM = int(os.getenv("RATE_LIMIT_TPM", "12000"))  # Tokens per minute

# ── INVESTMENT LIMITS ──────────────────────────────────────────────────────────

MIN_INVESTMENT = 100000  # Rs 1 Lakh
MAX_INVESTMENT = 100000000  # Rs 10 Crore
DICGC_LIMIT = 500000  # Rs 5 Lakhs per bank

# ── VALID PARAMETERS ──────────────────────────────────────────────────────────

VALID_TENURES = [3, 6, 9, 12, 18, 24]  # months
VALID_RISK_PROFILES = ["conservative", "moderate", "aggressive"]

TENURE_LABELS = {
    3: "3 months (Short-term)",
    6: "6 months (Short-medium)",
    9: "9 months (Medium)",
    12: "12 months (Standard)",
    18: "18 months (Medium-long)",
    24: "24 months (Long-term)"
}

RISK_LABELS = {
    "conservative": "Conservative (Low Risk, Lower Returns)",
    "moderate": "Moderate (Balanced Risk/Return)",
    "aggressive": "Aggressive (High Risk, Higher Returns)"
}

# ── PSO ALGORITHM PARAMETERS ──────────────────────────────────────────────────

PSO_NUM_PARTICLES = int(os.getenv("PSO_NUM_PARTICLES", "60"))
PSO_NUM_ITERATIONS = int(os.getenv("PSO_NUM_ITERATIONS", "200"))
PSO_INERTIA_WEIGHT = float(os.getenv("PSO_INERTIA_WEIGHT", "0.729"))
PSO_COGNITION_COEFF = float(os.getenv("PSO_COGNITION_COEFF", "1.494"))
PSO_SOCIAL_COEFF = float(os.getenv("PSO_SOCIAL_COEFF", "1.494"))

# PSO Risk concentration limits (max % of portfolio in single bank)
PSO_RISK_LIMITS = {
    "conservative": 0.20,   # 20% max in single bank
    "moderate": 0.35,       # 35% max
    "aggressive": 0.50      # 50% max
}

# ── BANK DATA ──────────────────────────────────────────────────────────────────

BANKS = [
    {
        "id": "suryoday",
        "name": "Suryoday Small Finance Bank",
        "type": "Small Finance Bank",
        "rating": "AA",
        "dicgc": True,
        "rates": {"3": 6.75, "6": 7.25, "9": 7.50, "12": 8.25, "18": 8.50, "24": 8.35}
    },
    {
        "id": "unity",
        "name": "Unity Small Finance Bank",
        "type": "Small Finance Bank",
        "rating": "AA",
        "dicgc": True,
        "rates": {"3": 6.50, "6": 7.00, "9": 7.35, "12": 8.15, "18": 8.40, "24": 8.20}
    },
    {
        "id": "utkarsh",
        "name": "Utkarsh Small Finance Bank",
        "type": "Small Finance Bank",
        "rating": "AA",
        "dicgc": True,
        "rates": {"3": 6.60, "6": 7.10, "9": 7.40, "12": 8.10, "18": 8.30, "24": 8.15}
    },
    {
        "id": "shivalik",
        "name": "Shivalik Small Finance Bank",
        "type": "Small Finance Bank",
        "rating": "A+",
        "dicgc": True,
        "rates": {"3": 6.40, "6": 6.90, "9": 7.25, "12": 8.00, "18": 8.20, "24": 8.00}
    },
    {
        "id": "shriram",
        "name": "Shriram Finance",
        "type": "NBFC",
        "rating": "AA+",
        "dicgc": False,
        "rates": {"3": 7.00, "6": 7.50, "9": 7.75, "12": 8.30, "18": 8.45, "24": 8.50}
    },
    {
        "id": "bajaj",
        "name": "Bajaj Finance",
        "type": "NBFC",
        "rating": "AAA",
        "dicgc": False,
        "rates": {"3": 7.15, "6": 7.60, "9": 7.80, "12": 8.35, "18": 8.50, "24": 8.55}
    },
    {
        "id": "mahindra",
        "name": "Mahindra Finance",
        "type": "NBFC",
        "rating": "AA+",
        "dicgc": False,
        "rates": {"3": 6.90, "6": 7.40, "9": 7.65, "12": 8.20, "18": 8.35, "24": 8.40}
    },
    {
        "id": "jana",
        "name": "Jana Small Finance Bank",
        "type": "Small Finance Bank",
        "rating": "A+",
        "dicgc": True,
        "rates": {"3": 6.30, "6": 6.85, "9": 7.20, "12": 7.90, "18": 8.10, "24": 7.95}
    }
]

# ── API CONFIGURATION ──────────────────────────────────────────────────────────

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = DEBUG
API_LOG_LEVEL = "info" if not DEBUG else "debug"

# ── LOGGING ────────────────────────────────────────────────────────────────────

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ── VALIDATION ──────────────────────────────────────────────────────────────────

def validate_amount(amount: float) -> bool:
    """Validate investment amount"""
    return MIN_INVESTMENT <= amount <= MAX_INVESTMENT


def validate_tenure(tenure: int) -> bool:
    """Validate tenure"""
    return tenure in VALID_TENURES


def validate_risk_profile(risk: str) -> bool:
    """Validate risk profile"""
    return risk in VALID_RISK_PROFILES


def get_config_summary() -> dict:
    """Get configuration summary for logging"""
    return {
        "environment": ENVIRONMENT,
        "debug": DEBUG,
        "llm_model": LLM_MODEL,
        "rate_limit_rpm": RATE_LIMIT_RPM,
        "pso_particles": PSO_NUM_PARTICLES,
        "pso_iterations": PSO_NUM_ITERATIONS,
        "api_host": API_HOST,
        "api_port": API_PORT,
    }


# ── PRINT CONFIG (for debugging) ───────────────────────────────────────────────

if __name__ == "__main__":
    import json
    print("\nConfiguration Summary:")
    print(json.dumps(get_config_summary(), indent=2))
