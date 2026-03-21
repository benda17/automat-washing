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
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    @app.middleware("http")
    async def vercel_api_path_prefix(request: Request, call_next):
        if not os.environ.get("VERCEL"):
            return await call_next(request)
        path = request.scope.get("path") or ""
        if not path or path.startswith("/api"):
            return await call_next(request)
        # Top-level document loads must reach StaticFiles (html=True), not /api/* JSON routes.
        sec_dest = request.headers.get("sec-fetch-dest")
        if sec_dest == "document":
            return await call_next(request)
        # Without Sec-Fetch-Dest (rare), only skip exact SPA paths — not /lessons/* (those can be API fetches).
        if request.method == "GET" and path in _SPA_GET_PATHS:
            return await call_next(request)
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

    # Vercel often invokes `api/index.py` with paths that omit the `/api` segment (e.g. /auth/login).
    # Duplicate routers at their natural prefixes (not /lessons — conflicts with SPA document URLs).
    if os.environ.get("VERCEL"):
        from app.api import admin, auth, course, me, meta, submissions

        app.include_router(auth.router)
        app.include_router(me.router)
        app.include_router(course.router)
        app.include_router(meta.router)
        app.include_router(admin.router)
        app.include_router(submissions.router)

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
