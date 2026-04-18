"""
LLM Configuration — Groq with Rate Limiting & Retry Logic
Groq Free Tier: 6000 tokens/minute (TPM)
Get API key at: https://console.groq.com
Compatible with CrewAI 1.x
"""

import os
import time
from dotenv import load_dotenv
from crewai import LLM
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

load_dotenv()


# Rate limiter: track requests per minute
class RateLimiter:
    def __init__(self, max_requests_per_minute: int = 300):
        """Set to 300 req/min (conservative for 6000 TPM limit)"""
        self.max_requests = max_requests_per_minute
        self.requests = []

    def wait_if_needed(self):
        """Block if we're about to exceed rate limit"""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [t for t in self.requests if now - t < 60]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(time.time())


_rate_limiter = RateLimiter(max_requests_per_minute=300)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry=retry_if_exception_type(Exception),
)
def _get_llm_with_retry(model: str, api_key: str):
    """Internal function with retry logic for Groq rate limits"""
    _rate_limiter.wait_if_needed()
    return LLM(
        model=f"groq/{model}",
        api_key=api_key,
        temperature=0.1,
        max_tokens=2048,
        timeout=60,
    )


def get_llm(model: str = "llama-3.3-70b-versatile"):
    """
    Returns a CrewAI-compatible Groq LLM instance with rate limiting & retry logic.
    
    Available Groq models (all FREE):
      - llama-3.3-70b-versatile  (smartest, recommended - 500 req/min)
      - llama-3.1-8b-instant     (fastest, lighter - 6000 TPM)
      - mixtral-8x7b-32768       (great for long context)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "\n\n❌ GROQ_API_KEY is not set!\n"
            "────────────────────────────────\n"
            "1. Go to https://console.groq.com\n"
            "2. Sign up (free, no credit card)\n"
            "3. Click API Keys → Create Key\n"
            "4. Copy the key (starts with gsk_)\n"
            "5. Set environment variable:\n"
            "   Windows: set GROQ_API_KEY=gsk_your_key_here\n"
            "   Mac/Linux: export GROQ_API_KEY=gsk_your_key_here\n"
            "   Or create .env file with: GROQ_API_KEY=gsk_your_key_here\n"
        )

    return _get_llm_with_retry(model, api_key)


def get_fast_llm():
    """Fastest model — use if hitting rate limits on default model"""
    return get_llm(model="llama-3.1-8b-instant")