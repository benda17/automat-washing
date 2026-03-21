import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import get_settings
from app.database import Base, engine

logger = logging.getLogger(__name__)


def _resolve_frontend_dist() -> Path | None:
    """Find the Vite `dist` folder (local dev, `vercel dev`, or bundled serverless layouts)."""
    override = (os.environ.get("AUTOWASH_FRONTEND_DIST") or "").strip()
    if override:
        p = Path(override).resolve()
        if p.is_dir() and (p / "index.html").is_file():
            return p

    here = Path(__file__).resolve()  # .../backend/app/main.py
    roots: list[Path] = [
        here.parent.parent.parent,
        Path.cwd(),
        Path("/var/task"),
    ]

    rels = (Path("frontend") / "dist", Path("dist"))
    seen: set[Path] = set()
    for root in roots:
        for rel in rels:
            try:
                cand = (root / rel).resolve()
            except OSError:
                continue
            if cand in seen:
                continue
            seen.add(cand)
            if cand.is_dir() and (cand / "index.html").is_file():
                return cand
    return None


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    origin_regex = (settings.cors_origin_regex or "").strip() or None
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:5173"],
        allow_origin_regex=origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    # On Vercel, the UI is copied to root `public/` at build time and served from the edge (see
    # vercel.json). If `frontend/dist` is still present in the function bundle (e.g. `vercel dev`),
    # mount it so deep links keep working.
    if os.environ.get("VERCEL"):
        dist = _resolve_frontend_dist()
        if dist is not None:
            app.mount("/", StaticFiles(directory=str(dist), html=True), name="spa")
        else:
            logger.warning(
                "VERCEL is set but frontend dist was not found; static UI must be served from "
                "`public/` (build should run: cp frontend/dist -> public/). API routes still work."
            )
    return app


app = create_app()
