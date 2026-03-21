# Automat Washing

Internal **15-day engineering bootcamp platform**: roadmap, lessons with embedded video, exercise submissions, **automatic grading**, optional **staff reviews**, and **readiness analytics**.

## Quick start (local)

### Backend

```powershell
cd backend
pip install -r requirements.txt
python seed.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

Default DB: **SQLite** file `backend/autowash.db`. Override with `DATABASE_URL` (Postgres URL supported).

**Note:** `python seed.py` **drops and recreates all database tables**, then inserts users and the full course graph (so local schema always matches the models). Optional sample submissions: set `AUTOWASH_SEED_DEMO_SUBMISSIONS=1` when running seed (off by default).

**Videos:** Each day’s embed is defined in `backend/app/seed_curriculum.py` as `PRIMARY_VIDEOS` — widely used YouTube tutorials (e.g. freeCodeCamp Linux, Traversy Git/React, TechWorld Nana Docker/Kubernetes, pytest course, system design intro). A matching “open on YouTube” link + short rationale is injected into lesson resources.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (often `http://localhost:5173`). The dev server **proxies** `/api` to `http://127.0.0.1:8010` (port **8010** avoids clashing with other apps that use **8000**).

**Login fails?** (1) Start the API on port **8010** (see command above). (2) From `backend/`, run `python seed.py` once. (3) The SQLite file is always resolved to `backend/autowash.db` even if you start uvicorn from the repo root. (4) If you use a non-Vite preview server, set `VITE_API_BASE=http://127.0.0.1:8010` in `frontend/.env`.

### Docker (Postgres + API + static UI)

```powershell
docker compose up --build
```

- UI: `http://localhost:8080` (nginx → `dist/` + `/api` proxy)  
- API (direct): `http://localhost:8000`

Set a strong `SECRET_KEY` in the environment for anything beyond your laptop.

> **Note:** `backend/docker-entrypoint.sh` must use **LF** line endings for Linux containers (see `.gitattributes`).

## Deploying to Vercel

The repo is set up for a **single Vercel project** at the **repository root** (not `frontend/` as the root directory):

- **`vercel.json`** — runs **`npm run build --prefix frontend`**, then bundles **`frontend/dist/**` into the Python serverless function** via **`functions.main.py.includeFiles`**. All browser traffic (including `/` and React Router paths) is handled by FastAPI, which **mounts** that folder with **`StaticFiles(..., html=True)`** when **`VERCEL`** is set.
- **`main.py`** (repo root) — Vercel’s FastAPI entry; adds `backend/` to `sys.path`. **`/api/*`** is served by the API routers; everything else is the Vite build from **`frontend/dist`**.
- **`requirements.txt`** (repo root) — same dependencies as `backend/requirements.txt` (flat list; Vercel’s parser does not support `-r` includes).

### Dashboard / CLI checklist

1. Import the Git repo in [Vercel](https://vercel.com/new) (or run `vercel` from the repo root). Leave **Root Directory** empty (`.`).
2. **Do not** set the project root to `frontend/` only — the API lives beside it.
3. **Environment variables** (Production + Preview as needed):

| Variable | Required | Notes |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Strong random string (e.g. `openssl rand -hex 32`). |
| `DATABASE_URL` | Strongly recommended | Hosted **Postgres** (Neon, Supabase, Vercel Postgres, etc.). SQLite on Vercel is forced to **`/tmp`** when `VERCEL` is set (ephemeral; resets on cold starts). |
| `CORS_ORIGINS` | Recommended for production | Your real site origin(s), comma-separated, e.g. `https://bootcamp.example.com`. |
| `CORS_ORIGIN_REGEX` | Optional | e.g. `https://.*\.vercel\.app` so **Preview** deployments can call the API without listing every preview URL. |

4. **Do not** set `VITE_API_BASE` for production: the UI should call **`/api` on the same origin**.
5. **Initial data:** with `DATABASE_URL` pointing at your hosted DB, run **`python seed.py`** from `backend/` on your machine (or any runner with network access to the DB) so tables, users, and curriculum exist. Vercel does not run `seed.py` automatically.

Vercel sets `VERCEL=1` automatically; the API uses it to **mount the bundled `frontend/dist`** and to pick a writable SQLite path only if you stay on SQLite (not recommended for real use). If the homepage returns `{"detail":"Not Found"}`, the UI bundle is missing: confirm the latest deployment **succeeded** and that **`includeFiles`** still matches **`frontend/dist/**`** after the Vite build.

**Limits:** serverless timeouts and cold starts apply; heavy grading runs close to hobby-tier time limits — upgrade the plan or host the API on a long-running service if you hit limits.

### Production deployment

- **URL:** [https://automat-washing.vercel.app/](https://automat-washing.vercel.app/)

In the Vercel project **Environment Variables**, set **`CORS_ORIGINS`** to `https://automat-washing.vercel.app` (no trailing slash) so the browser can call `/api` from that origin. Alternatively set **`CORS_ORIGIN_REGEX`** to `https://.*\.vercel\.app` to allow this host and other `*.vercel.app` previews.

## Users (6)

These are the accounts written by `seed.py` into the database. **Sign in with username + password** (case-insensitive username). `email` is optional on the user record for future contact fields; the cohort rows use username only. **Change passwords** before any real deployment.

| Name | Username (sign-in) | Role | Password |
| --- | --- | --- | --- |
| Nadav | `nadavb` | admin | `Aa123456` |
| Niv | `nivbs` | admin | `Aa123456` |
| Benda | `benda` | admin | `Aa123456` |
| Israel | `isr` | student | `Aa123456` |
| Gavriel | `gab` | student | `Aa123456` |
| Reuven | `rvn` | student | `Aa123456` |

**Grading:** In the mentor console, staff can open each submission (full text + prior reviews). If a manual score is **lower** than the latest automatic score, the API requires a **score change explanation** (at least 20 characters); that text is appended to the student-visible feedback under “Score change rationale.”

## Product overview

- **Students:** dashboard (today + pulse + readiness), 15-day roadmap, lesson pages (video, goals, resources, rubric), Markdown-friendly submissions, instant auto feedback, history of grades.
- **Teachers/admins:** mentor console — roster readiness, completion heatmap, queue of submissions with **auto-only** reviews, manual review composer, `PATCH` hooks for lessons/exercises.
- **Evaluation:** 12-dimension rubric (correctness through maintainability) with weighted overall score; per-exercise keyword/structure heuristics; humans layer narrative and overrides.

## Documentation in this repo

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — stack, flows, API summary, grading design, security notes.
- [`docs/EXERCISE_SOURCES.md`](docs/EXERCISE_SOURCES.md) — where exercise *ideas* were grounded (FastAPI docs, Hands-on React, K8s labs, system design primers, etc.).

## 15-day curriculum (summary)

| Day | Focus | Grading emphasis |
| --- | --- | --- |
| 1 | Linux filesystem & shell | Commands, safety, logs |
| 2 | Processes, logs, SSH mindset | Triage narrative |
| 3 | Git branches, commits, PRs | Hygiene & communication |
| 4 | Merge vs rebase policy | Tradeoffs |
| 5 | React/TS architecture | Boundaries & typing |
| 6 | Forms & validation | State & UX |
| 7 | Data fetching, a11y, async UI | State machine & WCAG |
| 8 | FastAPI + Pydantic | API shape & validation |
| 9 | Modular FastAPI, logging | Layering & observability |
| 10 | Python testing (pytest, TestClient) | Fixtures, HTTP tests |
| 11 | API contracts, pagination, Big-O | Edge cases & complexity |
| 12 | Docker | Dockerfile hardening |
| 13 | Kubernetes basics | Manifests & config |
| 14 | CI/CD + Rancher awareness | Pipeline & secrets |
| 15 | System design — URL shortener | Requirements → scale |

Full detail (videos, resources, briefs) lives in `backend/app/seed_curriculum.py`.

## Implementation phases (for your team)

1. **Setup** — Python + Node, env vars, seed script, SQLite/Postgres choice.  
2. **Backend** — models, auth, course graph, submissions, admin analytics.  
3. **Frontend** — shell, roadmap, lesson, submissions, role-gated admin.  
4. **Grading engine** — rubric weights, keyword hints, narrative templates.  
5. **Polish** — Docker/K8s examples, README, mentor workflow dry-runs.

## Future improvements

- Alembic migrations; refresh tokens; OIDC/SAML for corporate IdP.  
- File uploads + optional code-runner sandbox for executable checks.  
- Notifications (email/Slack) when submissions need human follow-up.  
- Per-cohort scheduling (unlock rules by calendar, not only ordering).  
- Rich text / MDX lessons edited in-app with version history.

## License

Internal training artifact — assign a license if you open-source it.
