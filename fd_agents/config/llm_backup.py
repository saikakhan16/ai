"""
LLM Configuration — Groq (Free, 500 tokens/sec)
Get your FREE API key at: https://console.groq.com
Compatible with CrewAI 1.x
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq


def get_llm(model: str = "llama-3.3-70b-versatile"):
    """
    Returns a Groq LLM instance.

    Free models on Groq (pick based on need):
      llama-3.3-70b-versatile  ← smartest, use for all agents (default)
      llama-3.1-8b-instant     ← fastest, use if hitting rate limits
      mixtral-8x7b-32768       ← great for long context
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "\n\n❌  GROQ_API_KEY is not set!\n"
            "────────────────────────────────\n"
            "1. Go to https://console.groq.com\n"
            "2. Sign up (free, no credit card)\n"
            "3. Click API Keys → Create Key\n"
            "4. Copy the key (starts with gsk_)\n"
            "5. In your terminal run:\n"
            "      Windows: set GROQ_API_KEY=gsk_your_key_here\n"
            "      Mac/Linux: export GROQ_API_KEY=gsk_your_key_here\n"
            "   OR create a .env file with: GROQ_API_KEY=gsk_your_key_here\n"
        )

    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=0.1,
        max_tokens=2048,
        timeout=60,
    )


def get_fast_llm():
    """Faster model for simple tasks — use if hitting rate limits"""
    return get_llm(model="llama-3.1-8b-instant")
