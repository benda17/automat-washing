from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Exercise, Review, ReviewComment, Submission, SubmissionStatus, User, UserRole
from app.schemas.submission import (
    ComposedFilePartOut,
    ComposeFromFilesResponse,
    ReviewCommentCreate,
    ReviewCommentOut,
    ReviewOut,
    SubmissionCreate,
    SubmissionOut,
)
from app.services.file_text import extract_text_from_upload
from app.services.grading_engine import evaluate_submission

router = APIRouter(prefix="/submissions")

_MAX_ANSWER_FILES = 12
_MAX_ANSWER_FILE_BYTES = 4 * 1024 * 1024
_MAX_COMBINED_CHARS = 190_000


@router.post("/compose-from-files", response_model=ComposeFromFilesResponse)
async def compose_answer_from_files(
    user: Annotated[User, Depends(get_current_user)],
    files: list[UploadFile] = File(
        ...,
        description="Code, plain text, Markdown, PDF, or DOCX (multiple files allowed)",
    ),
) -> ComposeFromFilesResponse:
    """Turn uploads into plain text blocks merged for the exercise answer field."""
    if user.role != UserRole.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can convert files into exercise answers",
        )
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload at least one file")
    if len(files) > _MAX_ANSWER_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"At most {_MAX_ANSWER_FILES} files per request",
        )
    parts: list[ComposedFilePartOut] = []
    blocks: list[str] = []
    for uf in files:
        raw = await uf.read()
        if len(raw) > _MAX_ANSWER_FILE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large (max {_MAX_ANSWER_FILE_BYTES // (1024 * 1024)} MiB): {uf.filename}",
            )
        fname = uf.filename or "unnamed"
        text, warn = extract_text_from_upload(fname, raw)
        safe_name = Path(fname).name
        parts.append(ComposedFilePartOut(filename=safe_name, text=text, warning=warn))
        if text.strip():
            blocks.append(f"### Uploaded file: `{safe_name}`\n\n{text.strip()}")
        elif warn:
            blocks.append(f"### Uploaded file: `{safe_name}`\n\n_{warn}_")
    combined = "\n\n---\n\n".join(blocks)
    if len(combined) > _MAX_COMBINED_CHARS:
        combined = combined[:_MAX_COMBINED_CHARS] + "\n\n…[truncated to stay under submission size limit]"
    return ComposeFromFilesResponse(parts=parts, combined=combined)


@router.post("", response_model=SubmissionOut)
def create_submission(
    body: SubmissionCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> SubmissionOut:
    if user.role != UserRole.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Use a student account to submit exercises",
        )

    ex = db.get(Exercise, body.exercise_id)
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    sub = Submission(
        exercise_id=ex.id,
        student_id=user.id,
        content=body.content,
        status=SubmissionStatus.submitted,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    result = evaluate_submission(
        body.content,
        exercise_title=ex.title,
        auto_eval_hints=ex.auto_eval_hints or {},
        rubric_weights=ex.rubric_weights or {},
    )
    review = Review(
        submission_id=sub.id,
        reviewer_id=None,
        is_auto=True,
        overall_score=result["overall_score"],
        dimension_scores=result["dimension_scores"],
        feedback=result["feedback"],
        strengths=result["strengths"],
        weaknesses=result["weaknesses"],
        improvements=result["improvements"],
        mentor_tone_notes=result["mentor_tone_notes"],
    )
    db.add(review)
    sub.status = SubmissionStatus.graded
    db.commit()
    db.refresh(sub)

    return _load_submission_out(db, sub.id, enrich=True)


def _reviews_comment_load() -> list:
    return [selectinload(Submission.reviews).selectinload(Review.comments).selectinload(ReviewComment.author)]


@router.post("/{submission_id}/reviews/{review_id}/comments", response_model=SubmissionOut)
def add_review_comment(
    submission_id: int,
    review_id: int,
    body: ReviewCommentCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> SubmissionOut:
    sub = db.scalars(
        select(Submission)
        .options(*_reviews_comment_load())
        .where(Submission.id == submission_id)
    ).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    staff = user.role in (UserRole.teacher, UserRole.admin)
    if sub.student_id != user.id and not staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    rev = db.scalars(select(Review).where(Review.id == review_id, Review.submission_id == submission_id)).first()
    if not rev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    db.add(ReviewComment(review_id=rev.id, author_id=user.id, body=body.body.strip()))
    db.commit()
    return _load_submission_out(db, submission_id, enrich=True)


@router.get("/mine", response_model=list[SubmissionOut])
def list_mine(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[SubmissionOut]:
    rows = db.scalars(
        select(Submission)
        .options(
            *_reviews_comment_load(),
            selectinload(Submission.exercise).selectinload(Exercise.lesson),
        )
        .where(Submission.student_id == user.id)
        .order_by(Submission.created_at.desc())
        .limit(50)
    ).all()
    return [_to_out(s, enrich=True) for s in rows]


@router.get("/{submission_id}", response_model=SubmissionOut)
def get_submission(
    submission_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> SubmissionOut:
    staff = user.role in (UserRole.teacher, UserRole.admin)
    opts = [
        *_reviews_comment_load(),
        selectinload(Submission.student),
        selectinload(Submission.exercise).selectinload(Exercise.lesson),
    ]
    sub = db.scalars(
        select(Submission).options(*opts).where(Submission.id == submission_id)
    ).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if sub.student_id != user.id and not staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return _to_out(sub, enrich=True)


def _admin_submission_load_options():
    return [
        *_reviews_comment_load(),
        selectinload(Submission.student),
        selectinload(Submission.exercise).selectinload(Exercise.lesson),
    ]


def _load_submission_out(db: Session, sid: int, *, enrich: bool = False) -> SubmissionOut:
    opts = _admin_submission_load_options() if enrich else _reviews_comment_load()
    sub = db.scalars(select(Submission).options(*opts).where(Submission.id == sid)).first()
    assert sub
    return _to_out(sub, enrich=enrich)


def _review_to_out(r: Review) -> ReviewOut:
    comments: list[ReviewCommentOut] = []
    loaded = r.comments if "comments" in r.__dict__ else []
    for c in sorted(loaded, key=lambda x: x.created_at):
        au = c.author
        comments.append(
            ReviewCommentOut(
                id=c.id,
                author_id=c.author_id,
                author_username=au.username,
                author_full_name=au.full_name,
                author_role=au.role,
                body=c.body,
                created_at=c.created_at,
            )
        )
    return ReviewOut(
        id=r.id,
        is_auto=r.is_auto,
        overall_score=r.overall_score,
        dimension_scores=r.dimension_scores,
        feedback=r.feedback,
        strengths=r.strengths,
        weaknesses=r.weaknesses,
        improvements=r.improvements,
        mentor_tone_notes=r.mentor_tone_notes,
        created_at=r.created_at,
        reviewer_id=r.reviewer_id,
        comments=comments,
    )


def _to_out(sub: Submission, *, enrich: bool = False) -> SubmissionOut:
    revs = sorted(sub.reviews, key=lambda r: r.created_at, reverse=True)

    student_username = student_email = student_full_name = exercise_title = lesson_title = None
    lesson_day_index: int | None = None
    if enrich:
        stu = sub.student
        if stu is not None:
            student_username = stu.username
            student_email = stu.email
            student_full_name = stu.full_name
        ex = sub.exercise
        if ex is not None:
            exercise_title = ex.title
            les = ex.lesson
            if les is not None:
                lesson_title = les.title
                lesson_day_index = les.day_index

    return SubmissionOut(
        id=sub.id,
        exercise_id=sub.exercise_id,
        student_id=sub.student_id,
        content=sub.content,
        status=sub.status,
        created_at=sub.created_at,
        reviews=[_review_to_out(r) for r in revs],
        student_username=student_username,
        student_email=student_email,
        student_full_name=student_full_name,
        exercise_title=exercise_title,
        lesson_title=lesson_title,
        lesson_day_index=lesson_day_index,
    )
