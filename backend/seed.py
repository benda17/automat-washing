"""Seed: users + full 15-day course. Run from `backend/`: python seed.py

Each run replaces all users (and their submissions/reviews/progress), then rebuilds the course graph.

Optional sample submissions (non-production): set AUTOWASH_SEED_DEMO_SUBMISSIONS=1
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_backend_root = Path(__file__).resolve().parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import (
    Course,
    Exercise,
    Lesson,
    Module,
    Review,
    Submission,
    SubmissionStatus,
    User,
    UserLessonProgress,
    UserRole,
)
from app.security import hash_password
from app.seed_curriculum import DAYS, MODULES
from app.services.grading_engine import evaluate_submission

# Cohort accounts: name, username, shared initial password (change in production).
_SEED_PASSWORD = "Aa123456"


def wipe_users_and_related(db: Session) -> None:
    """Remove all users and dependent rows (reviews, submissions, lesson progress)."""
    db.execute(delete(Review))
    db.execute(delete(Submission))
    db.execute(delete(UserLessonProgress))
    db.execute(delete(User))
    db.commit()


def seed_users(db: Session) -> None:
    users_spec = [
        ("Nadav", "nadavb", _SEED_PASSWORD, UserRole.admin),
        ("Niv", "nivbs", _SEED_PASSWORD, UserRole.admin),
        ("Benda", "benda", _SEED_PASSWORD, UserRole.admin),
        ("Israel", "isr", _SEED_PASSWORD, UserRole.student),
        ("Gavriel", "gab", _SEED_PASSWORD, UserRole.student),
        ("Reuven", "rvn", _SEED_PASSWORD, UserRole.student),
    ]
    for full_name, username, pw, role in users_spec:
        db.add(
            User(
                username=username,
                email=None,
                full_name=full_name,
                hashed_password=hash_password(pw),
                role=role,
            )
        )
    db.commit()


def wipe_course_content(db: Session) -> None:
    """Remove course graph and dependent progress/submissions (users stay)."""
    db.execute(delete(Review))
    db.execute(delete(Submission))
    db.execute(delete(UserLessonProgress))
    db.execute(delete(Exercise))
    db.execute(delete(Lesson))
    db.execute(delete(Module))
    db.execute(delete(Course))
    db.commit()


def seed_course(db: Session) -> None:
    wipe_course_content(db)

    course = Course(
        slug="bootcamp-15",
        title="Automat Washing — Engineering Bootcamp (15 days)",
        description=(
            "Intensive internal ramp: Linux/Git, React+TS, FastAPI (incl. dedicated testing day), Docker/Kubernetes, CI/CD, system design. "
            "~10 engineer-hours of structured work per day (see each lesson schedule)."
        ),
        duration_days=15,
    )
    db.add(course)
    db.flush()

    mod_map: dict[str, Module] = {}
    for m in MODULES:
        mod = Module(
            course_id=course.id,
            slug=m["slug"],
            title=m["title"],
            summary=m.get("summary"),
            sort_order=m["sort_order"],
        )
        db.add(mod)
        db.flush()
        mod_map[m["slug"]] = mod

    for day in DAYS:
        mod = mod_map[day["module"]]
        les = Lesson(
            module_id=mod.id,
            day_index=day["day_index"],
            slug=day["slug"],
            title=day["title"],
            summary=day["summary"],
            video_url=day.get("video_url"),
            key_concepts=day.get("key_concepts", []),
            resources=day.get("resources", []),
            learning_goals=day.get("learning_goals", []),
            deliverables=day.get("deliverables", []),
            evaluation_rubric=day.get("evaluation_rubric", []),
            exercise_brief=day.get("exercise_brief", ""),
            locked=False,
        )
        db.add(les)
        db.flush()
        exercises_list = day.get("exercises") or []
        for ex in exercises_list:
            db.add(
                Exercise(
                    lesson_id=les.id,
                    slug=ex["slug"],
                    title=ex["title"],
                    description=ex["description"],
                    difficulty=ex.get("difficulty", "medium"),
                    exercise_type=ex.get("exercise_type", "text"),
                    auto_eval_hints=ex.get("auto_eval_hints") or {},
                    rubric_weights=ex.get("rubric_weights") or {},
                    source_attribution=ex.get("source_attribution"),
                    sort_order=int(ex.get("sort_order", 0)),
                )
            )
    db.commit()


DEMO_DAY1_A = """## Linux navigation & permissions lab

### Commands
```bash
mkdir -p var/log/myapp && cd var/log/myapp
find .. -maxdepth 3 -name "*.log" 2>/dev/null
grep -i "error" app.log | tail -n 25
chmod 640 app.log
ls -la app.log
```

### Why chmod 640
World cannot read logs that may contain PII. Group read keeps on-call access without opening to every login.

### Permission error on a shared server
I check `ls -la` on file and each parent directory for execute bit, compare owner/group to the running service user, then adjust group or ACLs — never open logs to “everyone”.

### find + grep together
`find` narrows paths first; then `grep -r` only inside bounded dirs so we do not scan the whole filesystem.
"""


DEMO_DAY1_B = """## Part 2 — Linux logs and operations (Day 1 follow-on)

### A — Two failure scenarios

**Failure 1 — inode rotation break:** In **production**, logrotate uses `copytruncate` so the file path stays the same but the inode changes. Anything doing plain `tail -f` on the old inode sees silence even though the app still writes. **Measure**: log shipper bytes-per-minute, line rate, and “stale file handle” style errors from agents; **mitigation**: use `tail -F`, or journald/filebeat with path tracking, or `copytruncate` off with `create` + `USR1` to the app.

**Failure 2 — permission drift after deploy:** A deploy script unpacks as root and leaves `/var/log/myapp` owned by root with mode `750`. The service user can no longer append; logs silently fail or go to stderr only. **Measure**: monitor write errors from the app, disk growth on the log volume vs expected line volume, and **production** alerts on “log write denied”. **Mitigation**: systemd `User=` + `LogsDirectory=` or explicit `chown` in post-deploy; add a **test** in CI that runs the service user and touches the log path.

### B — One number

Assume 2 KB average log line, 500 lines/s at peak, retain 7 days compressed. Rough uncompressed: 500 × 86,400 × 7 ≈ 302M lines/week × 2 KB ≈ 600 GB/week before compression — order-of-magnitude **measure** for disk budgeting and whether we need sampling or remote aggregation.

### C — Five mitigations

1. Alert when log line rate drops >50% while request rate is flat (**production** signal vs traffic).
2. Runbook step: verify inode with `ls -li` and compare to agent cursor (**mitigation** for rotation bugs).
3. **Test** in CI: integration **test** that starts app as service user and asserts it can open the log file path.
4. **Test**: ansible/molecule or shell **test** that permissions on `/var/log/myapp` match manifest after deploy.
5. Structured JSON logs + max line size cap to protect the pipeline (**mitigation** for accidental log bombs).

### D — Two snippets

```bash
# post-rotate sanity in **production**
ls -li /var/log/myapp/app.log
journalctl -u myapp --since "5 min ago" | tail -n 20
```

```python
def test_service_user_can_write_log(tmp_path, monkeypatch):
    log_dir = tmp_path / "log"
    log_dir.mkdir()
    # **test** ensures deploy assumptions: service user writable path
    assert oct(log_dir.stat().st_mode)[-3:] in ("755", "775", "770")
```

This ties **failure** detection to **measure**ment, concrete **mitigation**, and automated **test** coverage for paths we saw break in real **production** systems.
"""


def seed_demo_submissions(db: Session) -> None:
    demo_student = db.scalars(select(User).where(User.username == "isr")).first()
    if not demo_student:
        return
    if db.scalars(select(Submission).where(Submission.student_id == demo_student.id).limit(1)).first():
        return

    les1 = db.scalars(select(Lesson).where(Lesson.day_index == 1).order_by(Lesson.id)).first()
    if not les1:
        return

    ex_list = db.scalars(select(Exercise).where(Exercise.lesson_id == les1.id).order_by(Exercise.sort_order)).all()
    if len(ex_list) < 2:
        return

    ulp = db.scalars(
        select(UserLessonProgress).where(
            UserLessonProgress.user_id == demo_student.id,
            UserLessonProgress.lesson_id == les1.id,
        )
    ).first()
    if ulp:
        ulp.completion_percent = 40
    else:
        db.add(
            UserLessonProgress(
                user_id=demo_student.id,
                lesson_id=les1.id,
                completion_percent=40,
                completed=False,
            )
        )

    samples = [(ex_list[0], DEMO_DAY1_A), (ex_list[1], DEMO_DAY1_B)]
    for ex, body in samples:
        sub = Submission(
            exercise_id=ex.id,
            student_id=demo_student.id,
            content=body,
            status=SubmissionStatus.submitted,
        )
        db.add(sub)
        db.flush()
        result = evaluate_submission(
            body,
            exercise_title=ex.title,
            auto_eval_hints=ex.auto_eval_hints or {},
            rubric_weights=ex.rubric_weights or {},
        )
        db.add(
            Review(
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
        )
        sub.status = SubmissionStatus.graded
    db.commit()


def main() -> None:
    from app.database import Base

    # Drop and recreate tables so schema changes apply without manual DB file deletion.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        wipe_users_and_related(db)
        seed_users(db)
        seed_course(db)
        if os.environ.get("AUTOWASH_SEED_DEMO_SUBMISSIONS", "").strip().lower() in ("1", "true", "yes"):
            seed_demo_submissions(db)
            print("Seed complete (course rebuilt; optional demo submissions applied if user had none).")
        else:
            print("Seed complete (course rebuilt).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
