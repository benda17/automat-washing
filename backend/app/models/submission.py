import enum
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SubmissionStatus(str, enum.Enum):
    submitted = "submitted"
    graded = "graded"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[SubmissionStatus] = mapped_column(Enum(SubmissionStatus), default=SubmissionStatus.submitted)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    exercise: Mapped["Exercise"] = relationship(back_populates="submissions")
    student: Mapped["User"] = relationship(back_populates="submissions")
    reviews: Mapped[list["Review"]] = relationship(back_populates="submission")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"))
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_auto: Mapped[bool] = mapped_column(Boolean, default=True)
    overall_score: Mapped[int] = mapped_column(Integer)
    dimension_scores: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    feedback: Mapped[str] = mapped_column(Text)
    strengths: Mapped[list[str]] = mapped_column(JSON, default=list)
    weaknesses: Mapped[list[str]] = mapped_column(JSON, default=list)
    improvements: Mapped[list[str]] = mapped_column(JSON, default=list)
    mentor_tone_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submission: Mapped["Submission"] = relationship(back_populates="reviews")
    reviewer: Mapped["User | None"] = relationship(
        back_populates="reviews_authored",
        foreign_keys=[reviewer_id],
    )
    comments: Mapped[list["ReviewComment"]] = relationship(
        back_populates="review",
        order_by="ReviewComment.created_at",
    )


class ReviewComment(Base):
    """Threaded replies on a review (student ↔ mentor discussion)."""

    __tablename__ = "review_comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    review: Mapped["Review"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="review_comments")


from app.models.course import Exercise  # noqa: E402
from app.models.user import User  # noqa: E402
