# Automat Washing — architecture notes

## Product definition

Automat Washing is an **internal 15-day engineering bootcamp platform**: structured lessons (goals, videos, resources, rubrics), exercise submissions, **automatic mentor-style first-pass grading**, optional **human mentor overlays**, and **readiness analytics** for staff.

### Roles

- **admin** — full access; same mentor console as teacher for this build.
- **teacher** — curriculum tweaks (lesson/exercise PATCH), analytics, manual reviews.
- **student** — roadmap, lessons, submissions, personal readiness.

### Core flows

1. Student signs in → dashboard shows **next day**, roadmap pulse, readiness, recent submissions.
2. Student opens lesson → consumes content → submits markdown write-up → **auto review** attached immediately.
3. Teacher opens **Mentor console** → sees roster readiness, heatmap, auto-only queue → posts **manual review** (additional `Review` row; human score preferred in readiness averages).

## Stack (and why)

| Layer | Choice | Rationale |
| --- | --- | --- |
| API | **FastAPI** | Typed routes, OpenAPI, fast iteration for internal tools. |
| ORM | **SQLAlchemy 2** | Mature relational modeling; works with SQLite locally and Postgres in Docker/K8s. |
| DB | **SQLite** (local) / **Postgres** (compose) | SQLite for zero-friction onboarding; Postgres for real multi-instance deploys. |
| Auth | **JWT bearer** | Stateless API; simple for SPAs and future mobile clients. |
| Passwords | **bcrypt** | Widely deployed, avoids passlib/bcrypt version skew on bleeding-edge Python. |
| UI | **React + TypeScript + Vite** | Team-standard SPA ergonomics; fast dev server. |
| Data fetching | **TanStack Query** | Cached server state for dashboards and lessons. |
| Containers | **Docker Compose** | One command for DB + API + static UI behind nginx. |
| K8s | **Example manifests** under `deploy/kubernetes/` | Shows how to run the API behind Services/Deployments with secrets. |

## Backend layout

- `app/main.py` — FastAPI app, CORS, lifespan table creation.
- `app/models/*` — Users, course graph, submissions, reviews, progress.
- `app/api/*` — Routers: `auth`, `me`, `course`, `lessons`, `submissions`, `admin`.
- `app/services/grading_engine.py` — Rubric-weighted heuristic auto-grader with narrative feedback.
- `app/services/readiness.py` — Readiness score + weak dimensions + admin analytics payload.
- `seed.py` / `seed_curriculum.py` — Six users + full 15-day graph (six graded exercises per lesson).

## API surface (summary)

- `POST /api/auth/login` → JWT.
- `GET /api/me` → profile.
- `GET /api/me/dashboard` → student/teacher dashboard payload.
- `GET /api/course/current` → nested modules/lessons with per-user completion flags.
- `GET /api/lessons/{id}` — lesson detail + exercises; lazily creates `UserLessonProgress`.
- `POST /api/lessons/{id}/complete` — marks completion.
- `POST /api/submissions` — student-only; creates `Submission`, runs auto grade, stores `Review`, sets `graded`.
- `GET /api/submissions/mine` / `GET /api/submissions/{id}`.
- `GET /api/admin/analytics`, `GET /api/admin/submissions/needs-human`, `POST /api/admin/submissions/{id}/review`, `PATCH` lesson/exercise editors.

## Grading engine

- **Dimensions** (0–100 each): correctness, code_quality, naming, architecture, readability, git_hygiene, documentation, complexity_awareness, best_practices, edge_cases, testing_effort, maintainability.
- **Weights**: defaults in `grading_engine.DEFAULT_WEIGHTS`; per-exercise overrides via `Exercise.rubric_weights` JSON.
- **Signals**: length vs `min_chars`, required/bonus keywords, anti-patterns, structural Markdown (headings/lists/fences), mentions of tests/git/docs/complexity.
- **Output**: overall score, per-dimension scores, strengths/weaknesses/improvements lists, long-form Markdown feedback + mentor tone note.

Human reviews should treat auto scores as **coaching signals**, not authoritative correctness for code execution tasks (write-ups only in v1).

## Database entities

`users`, `courses`, `modules`, `lessons`, `exercises`, `submissions`, `reviews`, `user_lesson_progress` — see models for columns. Videos/resources/rubrics live as JSON on `lessons` for iteration speed.

## Frontend architecture

- React Router layouts: **Shell** with role-aware nav.
- Pages: Login, Dashboard, Roadmap, Lesson (video + brief + submit), Submissions (feedback thread), Admin (analytics + manual review form).
- Styling: **Automat Washing** visual language (cyan rinse accents, Outfit + Figtree).

## Security notes (internal)

JWT `SECRET_KEY` must be rotated for any shared environment. Passwords are bcrypt-hashed. This build is **not** hardened for public internet exposure; add rate limiting, refresh tokens, and centralized IdP when moving beyond trusted cohorts.
