from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import require_roles
from app.models import Exercise, Lesson, Review, Submission, User, UserRole
from app.schemas.course import ExerciseUpdate, LessonUpdate
from app.schemas.submission import ManualReviewCreate, SubmissionOut
from app.services.readiness import admin_analytics
from app.api.submissions import _admin_submission_load_options, _load_submission_out, _to_out

router = APIRouter(prefix="/admin", dependencies=[Depends(require_roles(UserRole.teacher, UserRole.admin))])


@router.get("/analytics")
def analytics(db: Annotated[Session, Depends(get_db)]) -> dict:
    return admin_analytics(db)


@router.get("/submissions/needs-human", response_model=list[SubmissionOut])
def submissions_needing_human(
    db: Annotated[Session, Depends(get_db)],
) -> list[SubmissionOut]:
    """Submissions that only have auto reviews (mentor can layer manual feedback)."""
    rows = db.scalars(
        select(Submission)
        .options(*_admin_submission_load_options())
        .order_by(Submission.created_at.desc())
        .limit(200)
    ).all()
    out: list[SubmissionOut] = []
    for s in rows:
        if not s.reviews:
            continue
        has_human = any(not r.is_auto for r in s.reviews)
        if not has_human:
            out.append(_to_out(s, enrich=True))
    return out[:80]


@router.get("/submissions/all", response_model=list[SubmissionOut])
def all_submissions(
    db: Annotated[Session, Depends(get_db)],
) -> list[SubmissionOut]:
    rows = db.scalars(
        select(Submission)
        .options(*_admin_submission_load_options())
        .order_by(Submission.created_at.desc())
        .limit(200)
    ).all()
    return [_to_out(s, enrich=True) for s in rows]


@router.post("/submissions/{submission_id}/review", response_model=SubmissionOut)
def manual_review(
    submission_id: int,
    body: ManualReviewCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles(UserRole.teacher, UserRole.admin))],
) -> SubmissionOut:
    sub = db.scalars(
        select(Submission).options(selectinload(Submission.reviews)).where(Submission.id == submission_id)
    ).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    auto_revs = sorted([r for r in sub.reviews if r.is_auto], key=lambda r: r.created_at, reverse=True)
    ref_auto = auto_revs[0].overall_score if auto_revs else None
    if ref_auto is not None and body.overall_score < ref_auto:
        expl = (body.score_change_explanation or "").strip()
        if len(expl) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "When the manual score is below the latest automatic score, "
                    "provide score_change_explanation (at least 20 characters) describing why points were reduced."
                ),
            )

    feedback = body.feedback
    if body.mentor_tone_notes:
        feedback = f"{feedback}\n\n---\n**Mentor addendum:** {body.mentor_tone_notes}"
    if body.score_change_explanation and body.score_change_explanation.strip():
        feedback = (
            f"{feedback}\n\n---\n**Score change rationale:**\n{body.score_change_explanation.strip()}"
        )

    review = Review(
        submission_id=sub.id,
        reviewer_id=user.id,
        is_auto=False,
        overall_score=body.overall_score,
        dimension_scores=body.dimension_scores,
        feedback=feedback,
        strengths=body.strengths,
        weaknesses=body.weaknesses,
        improvements=body.improvements,
        mentor_tone_notes=body.mentor_tone_notes,
    )
    db.add(review)
    db.commit()
    return _load_submission_out(db, submission_id, enrich=True)


@router.patch("/lessons/{lesson_id}")
def patch_lesson(
    lesson_id: int,
    body: LessonUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    les = db.get(Lesson, lesson_id)
    if not les:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(les, k, v)
    db.commit()
    return {"ok": True}


@router.patch("/exercises/{exercise_id}")
def patch_exercise(
    exercise_id: int,
    body: ExerciseUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    ex = db.get(Exercise, exercise_id)
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(ex, k, v)
    db.commit()
    return {"ok": True}
