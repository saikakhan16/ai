import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fd_agents"))

from api_new import app  # noqa: F401 — re-exported for uvicorn
