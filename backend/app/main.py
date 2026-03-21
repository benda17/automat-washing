import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from app.api import api_router
from app.config import get_settings
from app.database import Base, engine

logger = logging.getLogger(__name__)

# Vercel `api/index.py` sometimes forwards ASGI paths without the `/api` prefix; our routers are
# mounted at `/api/...`. Prefix only known API roots so `/`, `/assets/*`, etc. stay unchanged.
_VERCEL_API_ROOTS = (
    "/auth",
    "/me",
    "/course",
    "/lessons",
    "/submissions",
    "/admin",
    "/meta",
)


def _resolve_frontend_dist() -> Path | None:
    """Find the Vite `dist` folder (local dev, `vercel dev`, or Vercel bundle via includeFiles)."""
    override = (os.environ.get("AUTOWASH_FRONTEND_DIST") or "").strip()
    if override:
        p = Path(override).resolve()
        if p.is_dir() and (p / "index.html").is_file():
            return p

    here = Path(__file__).resolve()  # .../backend/app/main.py
    repo_root = here.parent.parent.parent
    candidates: list[Path] = [
        Path("/var/task/frontend/dist"),
        Path("/var/task") / "frontend" / "dist",
        repo_root / "frontend" / "dist",
        Path.cwd() / "frontend" / "dist",
        Path.cwd() / "dist",
    ]
    seen: set[Path] = set()
    for cand in candidates:
        try:
            cand = cand.resolve()
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
    app = FastAPI(title=settings.app_name, lifespan=lifespan, redirect_slashes=False)

    @app.middleware("http")
    async def vercel_api_path_prefix(request: Request, call_next):
        if os.environ.get("VERCEL"):
            path = request.scope.get("path") or ""
            if path and not path.startswith("/api"):
                if any(path == r or path.startswith(f"{r}/") for r in _VERCEL_API_ROOTS):
                    request.scope["path"] = f"/api{path}"
        return await call_next(request)

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

    # On Vercel, `vercel.json` bundles `frontend/dist/**` into the Python function (`includeFiles`).
    # Mount the SPA so `/`, client routes, and hashed `/assets/*` are served from the same origin as `/api`.
    if os.environ.get("VERCEL"):
        dist = _resolve_frontend_dist()
        if dist is not None:
            app.mount("/", StaticFiles(directory=str(dist), html=True), name="spa")
        else:
            logger.error(
                "VERCEL is set but frontend/dist was not found inside the function bundle. "
                "Check vercel.json functions.api/index.py.includeFiles and that buildCommand produces frontend/dist."
            )
    return app


app = create_app()
