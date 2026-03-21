from fastapi import APIRouter

from app.api import admin, auth, course, lessons, me, meta, submissions

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(me.router, tags=["me"])
api_router.include_router(course.router, tags=["course"])
api_router.include_router(lessons.router, tags=["lessons"])
api_router.include_router(submissions.router, tags=["submissions"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(meta.router, tags=["meta"])
