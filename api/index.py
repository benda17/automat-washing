"""
Vercel serverless entry. Must live under `api/` so `vercel.json` `functions` patterns match.

Local API dev: use uvicorn from `backend/` (see README), not this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_backend = _root / "backend"
if _backend.is_dir():
    sys.path.insert(0, str(_backend))

from app.main import app  # noqa: E402

__all__ = ["app"]
