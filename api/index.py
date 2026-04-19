"""
Vercel Handler - Routes all API requests to FastAPI app
"""
import sys
import os

# Add fd_agents to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fd_agents'))

from api_new import app

# Export the FastAPI app for Vercel
__all__ = ['app']
