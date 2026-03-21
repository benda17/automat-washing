"""Aggregate readiness signals for admin dashboards."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Lesson, Review, Submission, SubmissionStatus, User, UserLessonProgress, UserRole


def weak_dimensions_for_user(db: Session, user_id: int, limit: int = 5) -> list[dict[str, Any]]:
    stmt = (
        select(Review)
        .join(Submission)
        .where(Submission.student_id == user_id)
        .order_by(Review.created_at.desc())
        .limit(40)
    )
    reviews = list(db.scalars(stmt))
    agg: dict[str, list[int]] = defaultdict(list)
    for r in reviews:
        for k, v in (r.dimension_scores or {}).items():
            if isinstance(v, (int, float)):
                agg[k].append(int(v))
    averages = {k: round(sum(vals) / len(vals)) for k, vals in agg.items() if vals}
    sorted_dims = sorted(averages.items(), key=lambda x: x[1])
    return [{"dimension": k, "avg_score": v} for k, v in sorted_dims[:limit]]


def student_readiness(db: Session, user: User) -> dict[str, Any]:
    if user.role != UserRole.student:
        return {"readiness_score": None, "note": "Not a student account"}

    total_lessons = db.scalar(select(func.count()).select_from(Lesson)) or 0
    completed = db.scalar(
        select(func.count())
        .select_from(UserLessonProgress)
        .where(UserLessonProgress.user_id == user.id, UserLessonProgress.completed.is_(True))
    ) or 0

    graded = db.scalars(
        select(Submission).where(Submission.student_id == user.id, Submission.status == SubmissionStatus.graded)
    ).all()
    latest_by_exercise: dict[int, Submission] = {}
    for s in sorted(graded, key=lambda x: x.created_at):
        latest_by_exercise[s.exercise_id] = s

    scores: list[int] = []
    for sub in latest_by_exercise.values():
        human = db.scalars(
            select(Review)
            .where(Review.submission_id == sub.id, Review.is_auto.is_(False))
            .order_by(Review.created_at.desc())
            .limit(1)
        ).first()
        auto = db.scalars(
            select(Review)
            .where(Review.submission_id == sub.id, Review.is_auto.is_(True))
            .order_by(Review.created_at.desc())
            .limit(1)
        ).first()
        rev = human or auto
        if rev:
            scores.append(rev.overall_score)

    avg_grade = round(sum(scores) / len(scores)) if scores else 0
    completion_pct = round(100 * completed / total_lessons) if total_lessons else 0

    # Weighted blend: completion drives habit; grades drive quality
    readiness = int(round(completion_pct * 0.45 + avg_grade * 0.45 + min(10, len(scores)) * 1.0))
    readiness = max(0, min(100, readiness))

    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "email": user.email,
        "lessons_completed": completed,
        "lessons_total": total_lessons,
        "completion_percent": completion_pct,
        "exercises_graded": len(scores),
        "average_grade": avg_grade,
        "readiness_score": readiness,
        "weak_dimensions": weak_dimensions_for_user(db, user.id),
    }


def admin_analytics(db: Session) -> dict[str, Any]:
    students = db.scalars(select(User).where(User.role == UserRole.student)).all()
    roster = [student_readiness(db, u) for u in students]

    recent = db.scalars(
        select(Submission)
        .options(selectinload(Submission.student), selectinload(Submission.exercise), selectinload(Submission.reviews))
        .order_by(Submission.created_at.desc())
        .limit(80)
    ).all()
    auto_only_queue = [s for s in recent if s.reviews and not any(not r.is_auto for r in s.reviews)]

    heatmap: list[dict[str, Any]] = []
    for u in students:
        progress_rows = db.scalars(select(UserLessonProgress).where(UserLessonProgress.user_id == u.id)).all()
        by_lesson = {p.lesson_id: p for p in progress_rows}
        lessons = db.scalars(select(Lesson).order_by(Lesson.day_index)).all()
        heatmap.append(
            {
                "user_id": u.id,
                "full_name": u.full_name,
                "days": [
                    {
                        "day": les.day_index,
                        "completed": bool(by_lesson.get(les.id) and by_lesson[les.id].completed),
                        "percent": by_lesson[les.id].completion_percent if by_lesson.get(les.id) else 0,
                    }
                    for les in lessons
                ],
            }
        )

    return {
        "students": roster,
        "auto_only_submissions": [
            {
                "id": s.id,
                "student": s.student.full_name,
                "exercise": s.exercise.title,
                "created_at": s.created_at.isoformat(),
            }
            for s in auto_only_queue[:40]
        ],
        "heatmap": heatmap,
    }
