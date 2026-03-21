from typing import Any

from pydantic import BaseModel, Field


class ExerciseOut(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    difficulty: str
    exercise_type: str
    source_attribution: str | None
    sort_order: int

    model_config = {"from_attributes": True}


class LessonSummaryOut(BaseModel):
    id: int
    day_index: int
    slug: str
    title: str
    summary: str
    locked: bool
    video_url: str | None
    completed: bool = False
    completion_percent: int = 0

    model_config = {"from_attributes": True}


class LessonDetailOut(LessonSummaryOut):
    key_concepts: list[Any]
    resources: list[Any]
    learning_goals: list[Any]
    deliverables: list[Any]
    evaluation_rubric: list[Any]
    exercise_brief: str
    exercises: list[ExerciseOut] = []


class ModuleOut(BaseModel):
    id: int
    slug: str
    title: str
    summary: str | None
    sort_order: int
    lessons: list[LessonSummaryOut] = []

    model_config = {"from_attributes": True}


class CourseOut(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None
    duration_days: int
    modules: list[ModuleOut] = []

    model_config = {"from_attributes": True}


class LessonUpdate(BaseModel):
    summary: str | None = None
    video_url: str | None = None
    key_concepts: list[Any] | None = None
    resources: list[Any] | None = None
    learning_goals: list[Any] | None = None
    deliverables: list[Any] | None = None
    evaluation_rubric: list[Any] | None = None
    exercise_brief: str | None = None
    locked: bool | None = None


class ExerciseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty: str | None = None
    auto_eval_hints: dict[str, Any] | None = None
    rubric_weights: dict[str, float] | None = None
    source_attribution: str | None = None
