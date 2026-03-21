from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Course, Lesson, Module, User, UserLessonProgress
from app.schemas import CourseOut, LessonSummaryOut, ModuleOut

router = APIRouter(prefix="/course")


def _lesson_summary(les: Lesson, user: User, db: Session) -> dict[str, Any]:
    prog = db.scalars(
        select(UserLessonProgress).where(
            UserLessonProgress.user_id == user.id, UserLessonProgress.lesson_id == les.id
        )
    ).first()
    return {
        "id": les.id,
        "day_index": les.day_index,
        "slug": les.slug,
        "title": les.title,
        "summary": les.summary,
        "locked": les.locked,
        "video_url": les.video_url,
        "completed": bool(prog and prog.completed),
        "completion_percent": prog.completion_percent if prog else 0,
    }


@router.get("/current", response_model=CourseOut)
def get_current_course(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> CourseOut:
    course = db.scalars(
        select(Course).order_by(Course.id).options(selectinload(Course.modules).selectinload(Module.lessons))
    ).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No course seeded")
    modules_out: list[ModuleOut] = []
    for mod in sorted(course.modules, key=lambda m: m.sort_order):
        lessons_data = [_lesson_summary(les, user, db) for les in sorted(mod.lessons, key=lambda l: l.day_index)]
        lessons_models = [LessonSummaryOut.model_validate(x) for x in lessons_data]
        modules_out.append(
            ModuleOut(
                id=mod.id,
                slug=mod.slug,
                title=mod.title,
                summary=mod.summary,
                sort_order=mod.sort_order,
                lessons=lessons_models,
            )
        )
    return CourseOut(
        id=course.id,
        slug=course.slug,
        title=course.title,
        description=course.description,
        duration_days=course.duration_days,
        modules=modules_out,
    )
