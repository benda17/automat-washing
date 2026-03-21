from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.submission import Submission

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, default=15)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    modules: Mapped[list["Module"]] = relationship(back_populates="course", order_by="Module.sort_order")


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    course: Mapped["Course"] = relationship(back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="module", order_by="Lesson.day_index")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"))
    day_index: Mapped[int] = mapped_column(Integer, index=True)
    slug: Mapped[str] = mapped_column(String(160), index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    key_concepts: Mapped[list[Any]] = mapped_column(JSON, default=list)
    resources: Mapped[list[Any]] = mapped_column(JSON, default=list)
    learning_goals: Mapped[list[Any]] = mapped_column(JSON, default=list)
    deliverables: Mapped[list[Any]] = mapped_column(JSON, default=list)
    evaluation_rubric: Mapped[list[Any]] = mapped_column(JSON, default=list)
    exercise_brief: Mapped[str] = mapped_column(Text, default="")
    locked: Mapped[bool] = mapped_column(Boolean, default=False)

    module: Mapped["Module"] = relationship(back_populates="lessons")
    exercises: Mapped[list["Exercise"]] = relationship(back_populates="lesson", order_by="Exercise.sort_order")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(160), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(32), default="medium")
    exercise_type: Mapped[str] = mapped_column(String(32), default="text")
    auto_eval_hints: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    rubric_weights: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    source_attribution: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    lesson: Mapped["Lesson"] = relationship(back_populates="exercises")
    submissions: Mapped[list["Submission"]] = relationship(back_populates="exercise")
