from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Course, Lesson, Module, Submission, User, UserLessonProgress
from app.schemas import UserOut
from app.services.readiness import student_readiness

router = APIRouter(prefix="/me")


@router.get("", response_model=UserOut)
def get_profile(user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return UserOut.model_validate(user)


@router.get("/dashboard")
def my_dashboard(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    course = db.scalars(
        select(Course).options(selectinload(Course.modules).selectinload(Module.lessons))
    ).first()

    if not course:
        return {"course": None, "today": None, "roadmap": [], "submissions": [], "readiness": None}

    modules = sorted(course.modules, key=lambda m: m.sort_order)
    all_lessons: list[Lesson] = []
    for m in modules:
        all_lessons.extend(sorted(m.lessons, key=lambda l: l.day_index))

    progress_rows = db.scalars(select(UserLessonProgress).where(UserLessonProgress.user_id == user.id)).all()
    by_lesson = {p.lesson_id: p for p in progress_rows}

    # Prefer next incomplete lesson by day_index
    next_lesson = None
    for les in all_lessons:
        p = by_lesson.get(les.id)
        if not p or not p.completed:
            next_lesson = les
            break

    roadmap = []
    for les in all_lessons:
        p = by_lesson.get(les.id)
        roadmap.append(
            {
                "day_index": les.day_index,
                "lesson_id": les.id,
                "title": les.title,
                "slug": les.slug,
                "locked": les.locked,
                "completed": bool(p and p.completed),
                "completion_percent": p.completion_percent if p else 0,
            }
        )

    subs = db.scalars(
        select(Submission)
        .where(Submission.student_id == user.id)
        .order_by(Submission.created_at.desc())
        .limit(15)
    ).all()

    readiness = student_readiness(db, user) if user.role.value == "student" else None

    return {
        "course": {"title": course.title, "slug": course.slug, "duration_days": course.duration_days},
        "today": (
            {
                "lesson_id": next_lesson.id,
                "day_index": next_lesson.day_index,
                "title": next_lesson.title,
                "slug": next_lesson.slug,
            }
            if next_lesson
            else None
        ),
        "roadmap": roadmap,
        "submissions": [
            {
                "id": s.id,
                "exercise_id": s.exercise_id,
                "status": s.status.value,
                "created_at": s.created_at.isoformat(),
            }
            for s in subs
        ],
        "readiness": readiness,
    }
