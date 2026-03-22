import importlib.util
import logging
import os
import stat
from contextlib import asynccontextmanager
from pathlib import Path

import anyio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Scope

from app.api import api_router
from app.config import get_settings
from app.database import Base, SessionLocal, engine

logger = logging.getLogger(__name__)


class SPAStaticFiles(StaticFiles):
    """Serve Vite `dist` like StaticFiles, but fall back to `index.html` for unknown paths.

    Starlette's ``html=True`` only adds directory ``index.html`` and optional ``404.html``;
    it does **not** implement client-router SPA fallback, which would otherwise 404 on ``/login`` etc.
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404 or not self.html:
                raise
            if scope["method"] not in ("GET", "HEAD"):
                raise
            full_path, st = await anyio.to_thread.run_sync(self.lookup_path, "index.html")
            if st is not None and stat.S_ISREG(st.st_mode):
                return self.file_response(full_path, st, scope)
            raise


def _vercel_seed_if_empty() -> None:
    """First cold start on Vercel often has an empty DB; seed default users + curriculum once."""
    if os.environ.get("AUTOWASH_SKIP_VERCEL_AUTO_SEED", "").strip().lower() in ("1", "true", "yes"):
        return
    from sqlalchemy import func, select

    from app.models import User

    db = SessionLocal()
    try:
        n = db.scalar(select(func.count()).select_from(User)) or 0
        if n:
            return
        backend_root = Path(__file__).resolve().parent.parent
        seed_path = backend_root / "seed.py"
        if not seed_path.is_file():
            logger.error("VERCEL auto-seed: seed.py not found at %s", seed_path)
            return
        spec = importlib.util.spec_from_file_location("autowash_seed", seed_path)
        if spec is None or spec.loader is None:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.seed_users(db)
        mod.seed_course(db)
        logger.warning(
            "VERCEL: database had 0 users; auto-seeded cohort + curriculum (incl. benda / Aa123456). "
            "Disable with AUTOWASH_SKIP_VERCEL_AUTO_SEED=1."
        )
    except IntegrityError:
        db.rollback()
        logger.info("VERCEL auto-seed skipped (parallel cold start or existing users).")
    except Exception:
        logger.exception("VERCEL auto-seed failed")
    finally:
        db.close()

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
    if os.environ.get("VERCEL"):
        _vercel_seed_if_empty()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    @app.middleware("http")
    async def vercel_lessons_api_prefix(request: Request, call_next):
        if not os.environ.get("VERCEL"):
            return await call_next(request)
        path = request.scope.get("path") or ""
        if not path.startswith("/lessons/") or path.startswith("/api/"):
            return await call_next(request)
        if request.headers.get("sec-fetch-dest") == "document":
            return await call_next(request)
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
            app.mount("/", SPAStaticFiles(directory=str(dist), html=True), name="spa")
        else:
            logger.error(
                "VERCEL is set but frontend/dist was not found inside the function bundle. "
                "Check vercel.json functions.api/index.py.includeFiles and that buildCommand produces frontend/dist."
            )
    return app


app = create_app()
