from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Lesson, User, UserLessonProgress
from app.schemas import ExerciseOut, LessonDetailOut, LessonSummaryOut

router = APIRouter(prefix="/lessons")


@router.get("/{lesson_id}", response_model=LessonDetailOut)
def get_lesson(
    lesson_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> LessonDetailOut:
    les = db.scalars(
        select(Lesson).options(selectinload(Lesson.exercises)).where(Lesson.id == lesson_id)
    ).first()
    if not les:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    prog = db.scalars(
        select(UserLessonProgress).where(
            UserLessonProgress.user_id == user.id, UserLessonProgress.lesson_id == les.id
        )
    ).first()
    if prog is None:
        prog = UserLessonProgress(user_id=user.id, lesson_id=les.id, completion_percent=5)
        db.add(prog)
        db.commit()
        db.refresh(prog)

    exercises = sorted(les.exercises, key=lambda e: e.sort_order)
    base = LessonSummaryOut(
        id=les.id,
        day_index=les.day_index,
        slug=les.slug,
        title=les.title,
        summary=les.summary,
        locked=les.locked,
        video_url=les.video_url,
        completed=bool(prog.completed),
        completion_percent=prog.completion_percent,
    )
    return LessonDetailOut(
        **base.model_dump(),
        key_concepts=les.key_concepts or [],
        resources=les.resources or [],
        learning_goals=les.learning_goals or [],
        deliverables=les.deliverables or [],
        evaluation_rubric=les.evaluation_rubric or [],
        exercise_brief=les.exercise_brief or "",
        exercises=[ExerciseOut.model_validate(ex) for ex in exercises],
    )


@router.post("/{lesson_id}/complete")
def mark_lesson_complete(
    lesson_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    les = db.get(Lesson, lesson_id)
    if not les:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    prog = db.scalars(
        select(UserLessonProgress).where(
            UserLessonProgress.user_id == user.id, UserLessonProgress.lesson_id == les.id
        )
    ).first()
    if not prog:
        prog = UserLessonProgress(user_id=user.id, lesson_id=les.id)
        db.add(prog)
    from datetime import datetime, timezone

    prog.completed = True
    prog.completion_percent = 100
    prog.completed_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}
