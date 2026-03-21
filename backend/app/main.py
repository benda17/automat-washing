import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import get_settings
from app.database import Base, engine


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

    # On Vercel, the root `main.py` serverless entry receives all paths; the static `outputDirectory`
    # is not used for the HTML/JS shell. Serve the Vite build from disk (bundled via vercel.json includeFiles).
    if os.environ.get("VERCEL"):
        dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
        if dist.is_dir():
            app.mount("/", StaticFiles(directory=str(dist), html=True), name="spa")
    return app


app = create_app()
