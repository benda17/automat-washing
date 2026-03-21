import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _resolve_sqlite_url(url: str) -> str:
    """
    Pin SQLite files to the backend package root so the API always uses the same DB as `python seed.py`,
    regardless of whether uvicorn was started from repo root or `backend/`.
    """
    if not url.startswith("sqlite:///"):
        return url
    rest = url.removeprefix("sqlite:///")
    if rest.startswith("./") or (not rest.startswith("/") and ":" not in rest[:3]):
        # Relative path (./file.db or file.db)
        name = rest.removeprefix("./")
        backend_root = Path(__file__).resolve().parent.parent
        path = (backend_root / name).resolve()
        return f"sqlite:///{path.as_posix()}"
    return url


def _engine():
    url = _resolve_sqlite_url(get_settings().database_url)
    # Vercel serverless filesystem is read-only except /tmp; default ./autowash.db would fail.
    if url.startswith("sqlite") and os.environ.get("VERCEL"):
        url = "sqlite:////tmp/autowash.db"
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


engine = _engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
