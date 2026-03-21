import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.submission import Review, ReviewComment, Submission


class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.student)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submissions: Mapped[list["Submission"]] = relationship(back_populates="student")
    reviews_authored: Mapped[list["Review"]] = relationship(
        back_populates="reviewer",
        foreign_keys="Review.reviewer_id",
    )
    review_comments: Mapped[list["ReviewComment"]] = relationship(back_populates="author")
