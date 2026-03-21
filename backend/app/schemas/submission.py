from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.user import UserRole
from app.models.submission import SubmissionStatus


class ReviewCommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=20_000)


class ReviewCommentOut(BaseModel):
    id: int
    author_id: int
    author_username: str
    author_full_name: str
    author_role: UserRole
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmissionCreate(BaseModel):
    exercise_id: int
    content: str = Field(min_length=20, max_length=200_000)


class ComposedFilePartOut(BaseModel):
    filename: str
    text: str
    warning: str | None = None


class ComposeFromFilesResponse(BaseModel):
    """Merged Markdown-ish text for pasting into the answer field."""

    parts: list[ComposedFilePartOut]
    combined: str


class ReviewOut(BaseModel):
    id: int
    is_auto: bool
    overall_score: int
    dimension_scores: dict[str, Any]
    feedback: str
    strengths: list[str]
    weaknesses: list[str]
    improvements: list[str]
    mentor_tone_notes: str | None
    created_at: datetime
    reviewer_id: int | None
    comments: list[ReviewCommentOut] = []

    model_config = {"from_attributes": True}


class SubmissionOut(BaseModel):
    id: int
    exercise_id: int
    student_id: int
    content: str
    status: SubmissionStatus
    created_at: datetime
    reviews: list[ReviewOut] = []
    student_username: str | None = None
    student_email: str | None = None
    student_full_name: str | None = None
    exercise_title: str | None = None
    lesson_title: str | None = None
    lesson_day_index: int | None = None

    model_config = {"from_attributes": True}


class ManualReviewCreate(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    dimension_scores: dict[str, int] = Field(default_factory=dict)
    feedback: str = Field(min_length=5, max_length=20_000)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    mentor_tone_notes: str | None = None
    score_change_explanation: str | None = Field(default=None, max_length=10_000)
