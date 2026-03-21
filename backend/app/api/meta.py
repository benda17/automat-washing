"""Lightweight catalog stats for mentors and tooling."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import Course, Exercise, Lesson, Module, User, UserRole

router = APIRouter(prefix="/meta")


@router.get("/curriculum")
def curriculum_overview(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.teacher, UserRole.admin))],
) -> dict:
    lessons = db.scalar(select(func.count()).select_from(Lesson)) or 0
    exercises = db.scalar(select(func.count()).select_from(Exercise)) or 0
    modules = db.scalar(select(func.count()).select_from(Module)) or 0
    course = db.scalars(select(Course).limit(1)).first()
    return {
        "app": "Automat Washing",
        "course_title": course.title if course else None,
        "duration_days": course.duration_days if course else 0,
        "modules": modules,
        "lessons": lessons,
        "exercises": exercises,
        "suggested_hours_per_day": 10,
        "suggested_total_hours": (course.duration_days * 10) if course else 0,
        "note": "Schedule blocks are guidance; adjust with your mentor.",
    }


@router.get("/curriculum/public")
def curriculum_public(db: Annotated[Session, Depends(get_db)]) -> dict:
    """Anonymous-friendly counts for landing (no auth)."""
    lessons = db.scalar(select(func.count()).select_from(Lesson)) or 0
    exercises = db.scalar(select(func.count()).select_from(Exercise)) or 0
    course = db.scalars(select(Course).limit(1)).first()
    return {
        "title": course.title if course else "Automat Washing",
        "days": course.duration_days if course else 15,
        "lessons": lessons,
        "exercises": exercises,
    }
