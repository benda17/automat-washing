"""
Vercel serverless entry: exposes the FastAPI `app` instance at the repository root.

Local development: run the API from `backend/` with uvicorn (see README), not this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent / "backend"
if _backend.is_dir():
    sys.path.insert(0, str(_backend))

from app.main import app  # noqa: E402

__all__ = ["app"]
