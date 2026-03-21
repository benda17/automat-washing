"""
15-day Automat Washing bootcamp content (~10h suggested per day). Exercise ideas synthesized from public curricula;
see docs/EXERCISE_SOURCES.md for citations (FastAPI tutorial, Hands-on React, K8s labs, pytest drills, etc.).
"""

from __future__ import annotations

from typing import Any

MODULES: list[dict[str, Any]] = [
    {
        "slug": "foundations",
        "title": "Foundations — Linux & Git",
        "summary": "Shell fluency, collaboration hygiene, and reviewable history.",
        "sort_order": 0,
    },
    {
        "slug": "frontend",
        "title": "Modern Frontend (React + TypeScript)",
        "summary": "Components, state, forms, async UI, accessibility, maintainability.",
        "sort_order": 1,
    },
    {
        "slug": "backend",
        "title": "Backend with Python & FastAPI",
        "summary": "API design, validation, structure, testing, production instincts.",
        "sort_order": 2,
    },
    {
        "slug": "platform",
        "title": "Platform, Delivery & System Design",
        "summary": "Containers, Kubernetes mindset, CI/CD, and design communication.",
        "sort_order": 3,
    },
]


def _ex(
    slug: str,
    title: str,
    description: str,
    *,
    difficulty: str = "medium",
    hints: dict[str, Any] | None = None,
    weights: dict[str, float] | None = None,
    attribution: str | None = None,
    sort_order: int = 0,
) -> dict[str, Any]:
    return {
        "slug": slug,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "exercise_type": "text",
        "auto_eval_hints": hints or {},
        "rubric_weights": weights or {},
        "source_attribution": attribution,
        "sort_order": sort_order,
    }


# Curated primary embeds: widely used tutorials with strong view counts / reputation (YouTube).
# watch= URL is for students who prefer opening YouTube directly.
PRIMARY_VIDEOS: dict[int, tuple[str, str, str]] = {
    1: (
        "https://www.youtube.com/embed/sWbUDq4S6Y8",
        "https://www.youtube.com/watch?v=sWbUDq4S6Y8",
        "freeCodeCamp.org + Linux Foundation — full “Introduction to Linux” course (millions of views; de‑facto standard intro).",
    ),
    2: (
        "https://www.youtube.com/embed/YS5Zh7KExvE",
        "https://www.youtube.com/watch?v=YS5Zh7KExvE",
        "Learn Linux TV — long-form SSH / remote access guide (hundreds of thousands of views; pairs with logs & service mindset).",
    ),
    3: (
        "https://www.youtube.com/embed/SWYqp7iY_Tc",
        "https://www.youtube.com/watch?v=SWYqp7iY_Tc",
        "Traversy Media — Git & GitHub crash course (~3M+ views; branches, commits, remotes in one sitting).",
    ),
    4: (
        "https://www.youtube.com/embed/CRlGDDprdOQ",
        "https://www.youtube.com/watch?v=CRlGDDprdOQ",
        "Academind — Git MERGE vs REBASE (~1M+ views; clear visual walkthrough of tradeoffs).",
    ),
    5: (
        "https://www.youtube.com/embed/w7ejDZ8SWv8",
        "https://www.youtube.com/watch?v=w7ejDZ8SWv8",
        "Traversy Media — React JS crash course (embed IDs are case-sensitive; this is the working ID).",
    ),
    6: (
        "https://www.youtube.com/embed/TPACABQTHvM",
        "https://www.youtube.com/watch?v=TPACABQTHvM",
        "ByteGrad — TypeScript in React crash course (large audience; props, hooks, generics).",
    ),
    7: (
        "https://www.youtube.com/embed/qdCHEUaFhBk",
        "https://www.youtube.com/watch?v=qdCHEUaFhBk",
        "Net Ninja (full React course series) — fetching data with useEffect (standard loading/error/data pattern).",
    ),
    8: (
        "https://www.youtube.com/embed/rvFsGRvj9jo",
        "https://www.youtube.com/watch?v=rvFsGRvj9jo",
        "Tech With Tim — FastAPI full crash course (very popular entry point to the framework).",
    ),
    9: (
        "https://www.youtube.com/embed/MCVcAAoDJS8",
        "https://www.youtube.com/watch?v=MCVcAAoDJS8",
        "Eric Roby / BrainBytes — FastAPI REST APIs with Python (clear structure, Swagger, CRUD).",
    ),
    10: (
        "https://www.youtube.com/embed/cHYq1MRoyI0",
        "https://www.youtube.com/watch?v=cHYq1MRoyI0",
        "freeCodeCamp.org — Testing Python with pytest (long-form, fixture/parametrize/mocking).",
    ),
    11: (
        "https://www.youtube.com/embed/6aDHWSNKlVw",
        "https://www.youtube.com/watch?v=6aDHWSNKlVw",
        "Big O notation & time-complexity tutorial (verified embed; vocabulary for APIs and interviews).",
    ),
    12: (
        "https://www.youtube.com/embed/pg19Z8LL06w",
        "https://www.youtube.com/watch?v=pg19Z8LL06w",
        "TechWorld with Nana — Docker crash course for beginners (~3M+ views; images, containers, Dockerfile).",
    ),
    13: (
        "https://www.youtube.com/embed/s_o8dwzRlu4",
        "https://www.youtube.com/watch?v=s_o8dwzRlu4",
        "TechWorld with Nana — Kubernetes crash course (~3.6M+ views; pods, deployments, services, demo app).",
    ),
    14: (
        "https://www.youtube.com/embed/YLtlz88zrLg",
        "https://www.youtube.com/watch?v=YLtlz88zrLg",
        "Popular CI/CD walkthrough — GitHub Actions pipelines, tests, and deployment mindset (high engagement).",
    ),
    15: (
        "https://www.youtube.com/embed/m8Icp_Cid5o",
        "https://www.youtube.com/watch?v=m8Icp_Cid5o",
        "Gaurav Sen / freeCodeCamp — system design for beginners (~1.8M+ views; APIs, DBs, scale vocabulary).",
    ),
}


_RAW_DAYS: list[dict[str, Any]] = [
    # Day 1
    {
        "module": "foundations",
        "day_index": 1,
        "slug": "d01-linux-filesystem-shell",
        "title": "Day 1 — Linux filesystem, navigation, and shell basics",
        "summary": "Own the terminal: paths, globbing, pipes, and safe file operations.",
        "video_url": "https://www.youtube.com/embed/sWbUDq4S6Y8",
        "key_concepts": [
            "absolute vs relative paths",
            "stdin/stdout/stderr and pipes",
            "permissions model (user/group/other)",
            "environment variables",
        ],
        "resources": [
            {"label": "Linux Filesystem Explained", "url": "https://www.linux.com/training-tutorials/linux-filesystem-explained/"},
            {"label": "GNU Coreutils manual", "url": "https://www.gnu.org/software/coreutils/manual/"},
        ],
        "learning_goals": [
            "Navigate a tree confidently with cd, ls, find",
            "Explain what chmod/chown change and when to use sudo",
            "Chain commands with pipes and redirect logs to files",
        ],
        "deliverables": [
            "Written lab notes with commands used and outputs summarized",
            "Short reflection on one mistake you almost made and how you caught it",
        ],
        "evaluation_rubric": [
            {"criterion": "Command correctness", "weight": 0.25},
            {"criterion": "Safety awareness (rm -rf, sudo)", "weight": 0.2},
            {"criterion": "Clarity of explanation", "weight": 0.25},
            {"criterion": "Use of logs and verification", "weight": 0.15},
            {"criterion": "Professional tone", "weight": 0.15},
        ],
        "exercise_brief": "Complete a guided shell session: create a project tree, search for a string in files, compress logs, and fix a permission issue. Document every command.",
        "exercise": _ex(
            "linux-shell-permissions-report",
            "Report: Linux navigation, search, and file permissions",
            """## Goal
Show you can navigate a Unix tree, search text in files, and reason about permissions the way you would on a server.

## Do this (WSL, Linux VM, or SSH)
1. Create a small folder tree (at least 3 levels) under your home directory or `/tmp`.
2. Add a text file that looks like a **log** (10+ lines). Use **grep** to find one substring.
3. Use **find** to locate that file by name pattern (not only `ls`).
4. Create a **permission** problem (e.g. directory not traversable) and fix it with **chmod** — stay away from world-writable modes.

## Paste in the answer
- **Commands:** bullets in run order (rough transcript is fine).
- **Production:** 2–4 sentences on why grep/find/chmod matter on a shared host.
- **Diagnosis:** how you would interpret a permission error from a real user.
- **One combo:** one sentence describing using **grep** and **find** together.

Use the words **chmod**, **grep**, **find**, **log**, and **permission** so the grader can match them.""",
            hints={
                "min_chars": 1150,
                "required_keywords": ["chmod", "grep", "find", "log", "permission"],
                "bonus_keywords": ["pipe", "ssh", "sudo", "heredoc"],
                "anti_patterns": ["rm -rf /", "chmod 777"],
            },
            attribution="Inspired by classic Linux fundamentals labs (navigation, find/grep, permissions).",
        ),
    },
    # Day 2
    {
        "module": "foundations",
        "day_index": 2,
        "slug": "d02-processes-ssh-logs",
        "title": "Day 2 — Processes, services, logs, and SSH mindset",
        "summary": "Observe running systems, read signals, and operate remote hosts safely.",
        "video_url": "https://www.youtube.com/embed/ltjVJWIOPaQ",
        "key_concepts": ["PID/PPID", "signals", "systemd units at a glance", "SSH keys", "tail/journal"],
        "resources": [
            {"label": "DigitalOcean: Linux process management", "url": "https://www.digitalocean.com/community/tutorials/how-to-use-ps-kill-and-nice-to-manage-processes-in-linux"},
            {"label": "SSH architecture overview", "url": "https://www.ssh.com/academy/ssh"},
        ],
        "learning_goals": [
            "Use ps/top to reason about CPU/memory",
            "Tail logs and correlate timestamps with user reports",
            "Describe how SSH keys reduce password risk",
        ],
        "deliverables": ["Incident-style writeup: symptom → commands → hypothesis → next step"],
        "evaluation_rubric": [
            {"criterion": "Observability", "weight": 0.3},
            {"criterion": "Safe remote ops", "weight": 0.25},
            {"criterion": "Structured debugging narrative", "weight": 0.25},
            {"criterion": "Risk awareness", "weight": 0.2},
        ],
        "exercise_brief": "Simulate a mini-incident on a VM or WSL: a stuck process or noisy log. Capture what you checked, in what order, and what you would automate next time.",
        "exercise": _ex(
            "processes-and-logs-investigation",
            "Write-up: investigate a process or log problem",
            """## Goal
Practice a short, credible on-call style triage using **process** tools and **log** evidence.

## Do this
Spend ~20 minutes (real or simulated): pick a noisy **log**, a stuck **process**, or a slow command. Use at least one **process** command (`ps`, `top`, `htop`, etc.) and one **log** read (`tail`, `journalctl`, file grep).

## Paste — use these exact headings
### Context
Who reported what, and what environment (local VM, staging, prod-like)?

### Signals & commands
Ordered list: what you ran and what you saw (include **SSH** only if you actually used it; otherwise say “would SSH here because…”).

### Evidence
Quote or paraphrase one **log** line that matters.

### Hypothesis
One sentence: most likely cause.

### Mitigation
What you did or would do next.

### Follow-ups
Automation, alert, or doc you would add.

Include the words **process**, **log**, **ssh**, and **hypothesis** in the body.""",
            hints={
                "min_chars": 1300,
                "required_keywords": ["process", "log", "ssh", "hypothesis"],
                "bonus_keywords": ["journalctl", "systemd", "signal", "tail"],
            },
            attribution="Patterned after on-call triage drills and Linux observability primers.",
        ),
    },
    # Day 3
    {
        "module": "foundations",
        "day_index": 3,
        "slug": "d03-git-collaboration",
        "title": "Day 3 — Git collaboration: branches, commits, PR mindset",
        "summary": "Small, reviewable changes with messages that tell a story.",
        "video_url": "https://www.youtube.com/embed/8JJ101D3knE",
        "key_concepts": ["branch per task", "atomic commits", "PR description template", "diff review"],
        "resources": [
            {"label": "Git Book — Branching", "url": "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell"},
            {"label": "Conventional Commits", "url": "https://www.conventionalcommits.org/en/v1.0.0/"},
        ],
        "learning_goals": [
            "Create a feature branch and open a PR with test plan",
            "Write conventional commit messages",
            "Review a teammate diff for risk",
        ],
        "deliverables": ["PR link or paste diff + self-review checklist"],
        "evaluation_rubric": [
            {"criterion": "Commit granularity", "weight": 0.25},
            {"criterion": "PR communication", "weight": 0.3},
            {"criterion": "Diff review quality", "weight": 0.25},
            {"criterion": "Git hygiene", "weight": 0.2},
        ],
        "exercise_brief": "Implement a tiny README improvement or docs fix in a branch. Open a PR (or describe it) with context, screenshots if UI, and rollback plan.",
        "exercise": _ex(
            "git-branch-commits-pull-request",
            "Describe your branch, commits, and pull request",
            """## Goal
Show you can name a **branch**, write reviewable **commit** messages, and describe a **pull request** like a teammate.

## Do this
Pick a tiny real or fake change (docs typo, README tweak). Do not skip the narrative even if you did not push to GitHub.

## Paste
1. **Branch name** you would use + one sentence why it matches team convention.
2. **Commits:** 2–3 **commit** message lines (Conventional Commits style encouraged).
3. **Pull request** description with: context, test plan, risk/rollback.
4. **Diff review:** bullet list of what you scan for in **Files changed** (API breaks, typos, secrets, tests).

Use the phrases **branch**, **pull request**, **commit**, and **diff** clearly.""",
            hints={
                "min_chars": 1100,
                "required_keywords": ["branch", "pull request", "commit", "diff"],
                "bonus_keywords": ["conventional", "revert", "rollback"],
            },
            attribution="Aligned with GitHub/GitLab PR best-practice guidance and Conventional Commits.",
        ),
    },
    # Day 4
    {
        "module": "foundations",
        "day_index": 4,
        "slug": "d04-merge-rebase",
        "title": "Day 4 — Merging vs rebasing, conflict resolution, history hygiene",
        "summary": "Choose strategies that match team risk tolerance.",
        "video_url": "https://www.youtube.com/embed/f1wnYdLEpgI",
        "key_concepts": ["merge commit", "rebase interactive", "conflict markers", "force-with-lease"],
        "resources": [
            {"label": "Atlassian merge vs rebase", "url": "https://www.atlassian.com/git/tutorials/merging-vs-rebasing"},
        ],
        "learning_goals": ["Explain when rebase is inappropriate", "Resolve a conflict deliberately", "Recover from a bad local state"],
        "deliverables": ["Decision memo: team policy recommendation with tradeoffs"],
        "evaluation_rubric": [
            {"criterion": "Tradeoff clarity", "weight": 0.35},
            {"criterion": "Safety (force-with-lease, backups)", "weight": 0.25},
            {"criterion": "Communication with teammates", "weight": 0.2},
            {"criterion": "Examples", "weight": 0.2},
        ],
        "exercise_brief": "Write a one-page policy for a hypothetical 6-person team: when to merge, when to squash, when to rebase. Include a failure story and the lesson learned.",
        "exercise": _ex(
            "team-git-merge-rebase-policy",
            "Team policy: merge, rebase, and conflicts",
            """## Goal
Write a one-page team policy so engineers know when to **merge**, when to **rebase**, and how to handle **conflict** without drama.

## Audience
A 6-person product team shipping daily.

## Paste — sections
### Principles
2–3 bullets (shared main, protected branches, etc.).

### Rules
When **merge** is default; when **rebase** is allowed; when it is forbidden.

### Exceptions
Hotfix, release branch, or bot — spell out **tradeoff**s.

### Tooling & safety
At least one habit (e.g. `pull --rebase`, backup branch, `force-with-lease` policy).

### On-call impact
How bad history hurts incident response.

Name a real or fictional **conflict** story and the lesson. Use the words **rebase**, **merge**, **conflict**, and **tradeoff**.""",
            hints={
                "min_chars": 1150,
                "required_keywords": ["rebase", "merge", "conflict", "tradeoff"],
                "bonus_keywords": ["force-with-lease", "squash", "backup"],
            },
            attribution="Based on common team git policy discussions and Atlassian/Git docs.",
        ),
    },
    # Day 5
    {
        "module": "frontend",
        "day_index": 5,
        "slug": "d05-react-architecture",
        "title": "Day 5 — React + TypeScript architecture & components",
        "summary": "Composable UI boundaries and prop contracts.",
        "video_url": "https://www.youtube.com/embed/w7ejDZ8SWv8",
        "key_concepts": ["component boundaries", "composition", "TypeScript props", "folder structure"],
        "resources": [
            {"label": "React docs — Thinking in React", "url": "https://react.dev/learn/thinking-in-react"},
            {"label": "TypeScript handbook", "url": "https://www.typescriptlang.org/docs/handbook/intro.html"},
        ],
        "learning_goals": ["Decompose a screen into components", "Justify state placement", "Type a small props API"],
        "deliverables": ["ASCII or Mermaid component tree + rationale"],
        "evaluation_rubric": [
            {"criterion": "Architecture clarity", "weight": 0.3},
            {"criterion": "Type safety thinking", "weight": 0.25},
            {"criterion": "Reusability", "weight": 0.2},
            {"criterion": "Maintainability", "weight": 0.25},
        ],
        "exercise_brief": "Design (on paper) a dashboard widget: break it into presentational vs container concerns.",
        "exercise": _ex(
            "react-dashboard-component-tree",
            "Design the React component tree for a dashboard widget",
            """## Goal
Decompose one dashboard **component** into smaller pieces with clear **props** and **TypeScript** types.

## Pick a widget
e.g. “orders table with filters”, “user profile card”, “notification bell”.

## Paste
1. **Tree:** nested bullets or ASCII showing parent/children.
2. **Props:** TypeScript-style interfaces for 2 important **component**s (fields + types).
3. **State:** where **state** lives and why (local vs lifted).
4. **Decoupling:** 5 bullets — what you refuse to **couple** (routing, global store, fetch client, etc.).
5. **Async placeholders:** how **loading** and **error** UI hooks will attach later.

Use the words **component**, **props**, **state**, and **typescript** (or TypeScript).""",
            hints={
                "min_chars": 1100,
                "required_keywords": ["component", "props", "state", "typescript"],
                "bonus_keywords": ["composition", "accessibility", "aria"],
                "expects_code_fence": True,
            },
            attribution="Exercises mirror React.dev “Thinking in React” and component design practice.",
        ),
    },
    # Day 6
    {
        "module": "frontend",
        "day_index": 6,
        "slug": "d06-forms-state-validation",
        "title": "Day 6 — Forms, validation, and state management patterns",
        "summary": "Controlled inputs, reducers, and validation UX.",
        "video_url": "https://www.youtube.com/embed/6ThXsUwLWvc",
        "key_concepts": ["controlled components", "touched/dirty", "useReducer", "schema validation"],
        "resources": [
            {"label": "Hands-on React — Form Validation (TS)", "url": "https://handsonreact.com/docs/labs/ts/FormValidation"},
            {"label": "React docs — Forms", "url": "https://react.dev/reference/react-dom/components/input"},
        ],
        "learning_goals": ["Validate on blur vs submit", "Surface field-level errors", "Avoid unnecessary re-renders"],
        "deliverables": ["Pseudocode or snippet for a signup form hook"],
        "evaluation_rubric": [
            {"criterion": "Validation UX", "weight": 0.3},
            {"criterion": "State design", "weight": 0.3},
            {"criterion": "Error handling", "weight": 0.2},
            {"criterion": "Testing mindset", "weight": 0.2},
        ],
        "exercise_brief": "Specify a registration form: fields, validators, async email check sketch.",
        "exercise": _ex(
            "signup-form-validation-design",
            "Design signup form state, validation, and submit flow",
            """## Goal
Design signup **form** **state** with **validation**, **error** display, and **submit** flow in **TypeScript**-flavored React.

## Paste
1. Pseudocode or interface for `useSignupForm` returning `{ values, errors, touched, isSubmitting, ... }`.
2. When you validate: on blur, on change, on **submit** — pick and justify.
3. How you render field-level **error** messages (and disabled **submit** rules).
4. Sketch async email uniqueness check: loading state + **error** if taken.

Put code-ish blocks in fenced markdown. Use **validation**, **error**, **typescript**, and **submit** in prose.""",
            hints={
                "min_chars": 1150,
                "required_keywords": ["validation", "error", "typescript", "submit"],
                "bonus_keywords": ["useReducer", "async", "touched"],
                "expects_code_fence": True,
            },
            attribution="Informed by Hands-on React Lab 16 (form validation patterns).",
        ),
    },
    # Day 7
    {
        "module": "frontend",
        "day_index": 7,
        "slug": "d07-data-fetching-a11y",
        "title": "Day 7 — Data fetching, loading/error states, accessibility",
        "summary": "Professional async UI and inclusive defaults.",
        "video_url": "https://www.youtube.com/embed/4UZrsTqkcW4",
        "key_concepts": ["fetch lifecycle", "discriminated unions for UI state", "focus management", "reduced motion"],
        "resources": [
            {"label": "MDN — fetch", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch"},
            {"label": "WCAG quick reference", "url": "https://www.w3.org/WAI/WCAG21/quickref/"},
        ],
        "learning_goals": ["Model remote data states explicitly", "Design skeleton vs spinner tradeoffs", "Audit one WCAG criterion"],
        "deliverables": ["Checklist for shipping a data-heavy component"],
        "evaluation_rubric": [
            {"criterion": "Async correctness", "weight": 0.3},
            {"criterion": "UX polish", "weight": 0.25},
            {"criterion": "Accessibility", "weight": 0.25},
            {"criterion": "Testing plan", "weight": 0.2},
        ],
        "exercise_brief": "Design a table that loads paginated API data. Include empty, loading, error, and success.",
        "exercise": _ex(
            "async-table-loading-error-accessibility",
            "Plan loading, error, and success states for a data table",
            """## Goal
Model **fetch**/**loading**/**error** UI explicitly and tie it to **accessibility**.

## Scenario
Paginated table: user changes page, filter, or sort — remote **fetch** each time.

## Paste
1. **States:** `idle` / `loading` / `success` / `error` — bullet each with what the user sees.
2. **Transitions:** what event moves you between states (include at least one **error** retry path).
3. **Accessibility:** **aria**-busy, live region, or focus — pick what fits and say why.
4. **Compare:** 4 bullets — manual `useEffect` **fetch** vs TanStack Query (or SWR) for this table.

Use the words **loading**, **error**, **accessibility**, and **fetch** in the narrative.""",
            hints={
                "min_chars": 1500,
                "required_keywords": ["loading", "error", "accessibility", "fetch"],
                "bonus_keywords": ["aria", "retry", "timeout", "edge case"],
            },
            attribution="Combines common React async patterns with WCAG-oriented UI reviews.",
        ),
    },
    # Day 8
    {
        "module": "backend",
        "day_index": 8,
        "slug": "d08-fastapi-foundation",
        "title": "Day 8 — FastAPI foundations & Pydantic modeling",
        "summary": "Typed APIs with automatic docs and honest validation errors.",
        "video_url": "https://www.youtube.com/embed/9YBAUf5cyLA",
        "key_concepts": ["routes", "dependency injection preview", "Pydantic v2 models", "OpenAPI"],
        "resources": [
            {"label": "FastAPI Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"},
            {"label": "Real Python — FastAPI intro", "url": "https://realpython.com/fastapi-python-web-apis/"},
        ],
        "learning_goals": ["Create CRUD-shaped endpoints", "Return correct status codes", "Explain validation errors to clients"],
        "deliverables": ["OpenAPI screenshot or pasted path operations"],
        "evaluation_rubric": [
            {"criterion": "API shape", "weight": 0.3},
            {"criterion": "Validation rigor", "weight": 0.25},
            {"criterion": "Documentation", "weight": 0.2},
            {"criterion": "Error handling", "weight": 0.25},
        ],
        "exercise_brief": "Sketch a Task API: models, routes, and example 422.",
        "exercise": _ex(
            "fastapi-task-api-with-pydantic",
            "Sketch a Task API with FastAPI and Pydantic",
            """## Goal
Sketch a small **FastAPI** service with **Pydantic** models and honest **validation** errors.

## Paste (Python fenced blocks)
1. Models for `Task` (id, title, done, due optional).
2. At least three routes: list, create, patch done flag (or delete).
3. One example JSON body that would return **422** and why.
4. File layout: what stays in `main.py` vs **router** modules.

## Short prose
- How you expose **OpenAPI** / Swagger to QA.
- One **validation** **edge case** (empty title, future date, etc.).

Use **fastapi**, **pydantic**, **openapi**, and **validation** in text.""",
            hints={
                "min_chars": 1150,
                "required_keywords": ["fastapi", "pydantic", "openapi", "validation"],
                "bonus_keywords": ["422", "router", "status"],
                "expects_code_fence": True,
            },
            attribution="Grounded in the official FastAPI tutorial and CRUD examples.",
        ),
    },
    # Day 9
    {
        "module": "backend",
        "day_index": 9,
        "slug": "d09-modular-fastapi",
        "title": "Day 9 — Modular FastAPI, errors, logging, configuration",
        "summary": "Code layout that survives the first real feature.",
        "video_url": "https://www.youtube.com/embed/7V0sxpjAxxQ",
        "key_concepts": ["APIRouter", "settings via env", "HTTPException vs domain errors", "structured logs"],
        "resources": [
            {"label": "FastAPI Bigger Applications", "url": "https://fastapi.tiangolo.com/tutorial/bigger-applications/"},
        ],
        "learning_goals": ["Split routers by domain", "Centralize settings", "Log with context"],
        "deliverables": ["Proposed folder tree for a service"],
        "evaluation_rubric": [
            {"criterion": "Architecture", "weight": 0.3},
            {"criterion": "Observability", "weight": 0.25},
            {"criterion": "Configuration", "weight": 0.2},
            {"criterion": "Maintainability", "weight": 0.25},
        ],
        "exercise_brief": "Propose modules for `auth`, `catalog`, `orders` in one repo.",
        "exercise": _ex(
            "fastapi-folders-logging-errors",
            "Propose backend folders, logging, and error handling",
            """## Goal
Propose a **module** layout for `auth`, `catalog`, `orders` and show how **log**ging and errors cross **layer**s.

## Paste
1. **Tree:** ASCII folder structure (e.g. `app/routers`, `app/services`, `app/models`).
2. **Routers:** one sentence each on what each **router** owns.
3. **Errors:** how `HTTPException` vs domain errors map to responses.
4. **Logging:** what each **layer** logs (request id, user id, query duration).
5. **Config:** env vars vs secrets (where `.env` is OK vs not).

Use **router**, **log**, **layer**, and **module** in the answer.""",
            hints={
                "min_chars": 1500,
                "required_keywords": ["router", "log", "layer", "module"],
                "bonus_keywords": ["correlation", "trace", "secret"],
            },
            attribution="Follows FastAPI larger-application guidance and common clean-ish service layouts.",
        ),
    },
    # Day 10
    {
        "module": "backend",
        "day_index": 10,
        "slug": "d10-python-testing-pytest",
        "title": "Day 10 — Python testing: pytest, fixtures, and FastAPI TestClient",
        "summary": "Automated checks that survive refactors: unit + HTTP-level tests with pytest.",
        "video_url": "https://www.youtube.com/embed/cHYq1MRoyI0",
        "key_concepts": ["pytest", "fixture", "TestClient", "parametrize", "dependency overrides"],
        "resources": [
            {"label": "FastAPI — Testing", "url": "https://fastapi.tiangolo.com/tutorial/testing/"},
            {"label": "pytest — Getting started", "url": "https://docs.pytest.org/en/stable/getting-started.html"},
            {"label": "pytest fixtures", "url": "https://docs.pytest.org/en/stable/how-to/fixtures.html"},
            {"label": "Real Python — pytest", "url": "https://realpython.com/pytest-python-testing/"},
            {"label": "GitHub: pytest exercises (search)", "url": "https://github.com/search?q=pytest+exercises&type=repositories"},
        ],
        "learning_goals": [
            "Run pytest and read failures like a debugger",
            "Use TestClient to assert status codes and JSON bodies",
            "Name tests so the next engineer understands intent",
        ],
        "deliverables": ["Written test list + at least one code or pseudocode block using TestClient"],
        "evaluation_rubric": [
            {"criterion": "pytest mechanics", "weight": 0.3},
            {"criterion": "Fixtures & isolation", "weight": 0.25},
            {"criterion": "HTTP assertions", "weight": 0.25},
            {"criterion": "Clarity & maintainability", "weight": 0.2},
        ],
        "exercise_brief": "Design pytest tests for a small FastAPI list endpoint using TestClient, fixtures, and one parametrized case.",
        "exercise": _ex(
            "pytest-fastapi-testclient",
            "Write pytest tests using FastAPI’s TestClient",
            """## Goal
Show you can test an HTTP API with **pytest** and FastAPI’s **TestClient** (official pattern).

## Skim first
- [FastAPI — Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest — Getting started](https://docs.pytest.org/en/stable/getting-started.html)
- Optional repos: GitHub search `pytest-exercises`, or ChristopherGS **ultimate-fastapi-tutorial** (testing sections).

## Imaginary API (keep it tiny)
`GET /items` returns JSON `{"items": [...], "total": <int>}` and accepts `limit` and `offset` query params (integers).

## Do this in your answer
1. Paste **either** real Python **test** code **or** clearly labeled pseudocode that imports `TestClient` from `fastapi.testclient`.
2. List **at least four** **test** functions whose names read like behavior (`test_empty_list_returns_zero_total`, etc.).
3. Describe **one** **pytest** **fixture** (e.g. `client`, `app`, fake DB) — what it sets up and what it yields.
4. Show **one** `@pytest.mark.parametrize` example (status code or query string matrix).

## Also include
- A bullet **test list**: name → behavior locked in.
- One paragraph: what you would **not** assert at the HTTP layer (and where those asserts belong instead).

Mention **pytest**, **fixture**, **testclient**, and **test** in plain text (imports/paths count for **testclient**).""",
            hints={
                "min_chars": 1300,
                "required_keywords": ["pytest", "fixture", "testclient", "test"],
                "bonus_keywords": ["parametrize", "dependency", "override", "422", "status"],
                "expects_code_fence": True,
            },
            attribution="Follows FastAPI testing tutorial + pytest docs; optional drills from public pytest exercise repos on GitHub.",
        ),
    },
    # Day 11
    {
        "module": "backend",
        "day_index": 11,
        "slug": "d11-api-contracts-pagination-complexity",
        "title": "Day 11 — API contracts, pagination edge cases, and Big-O instinct",
        "summary": "Test plans for real query parameters plus complexity vocabulary for hot paths.",
        "video_url": "https://www.youtube.com/embed/6aDHWSNKlVw",
        "key_concepts": ["pagination contracts", "edge cases", "pytest naming", "Big-O vocabulary", "breaking changes"],
        "resources": [
            {"label": "FastAPI Testing (recap)", "url": "https://fastapi.tiangolo.com/tutorial/testing/"},
            {"label": "Mozilla — Big O (read)", "url": "https://developer.mozilla.org/en-US/docs/Glossary/Big_O_notation"},
            {"label": "FastAPI — Bigger applications", "url": "https://fastapi.tiangolo.com/tutorial/bigger-applications/"},
        ],
        "learning_goals": [
            "Enumerate pagination and filter failure modes before coding",
            "Relate DB work to Big-O at a high level",
            "Describe a backward-compatible API change",
        ],
        "deliverables": ["8+ test ideas + complexity paragraph + contract notes"],
        "evaluation_rubric": [
            {"criterion": "Edge-case coverage", "weight": 0.3},
            {"criterion": "Complexity reasoning", "weight": 0.25},
            {"criterion": "Contract clarity", "weight": 0.25},
            {"criterion": "Communication", "weight": 0.2},
        ],
        "exercise_brief": "Write a pytest-oriented test plan for a filtered, paginated product list and analyze complexity.",
        "exercise": _ex(
            "paginated-api-tests-and-big-o",
            "Test plan and Big-O notes for a paginated list API",
            """## Goal
Combine **pagination** **edge case** thinking with **complexity** vocabulary for a list endpoint.

## Endpoint
`GET /products?offset=0&limit=20&sort=price&category=shoes` → `{ "items": [...], "total": <int>, "page_info": {...} }`.

## Part A — **pytest** test plan
List **at least eight** **test** function names + one line intent each. Must include:
- happy path
- empty catalog
- `limit=0` or max limit cap
- **offset** past the end
- invalid **`sort`** field
- weird but safe **`category`** string (treated as literal data)
- two equal **`sort`** keys (stable ordering expectation)
- malformed numeric query param → expect **422** or your chosen error

## Part B — **complexity**
In 4–6 sentences: Big-O style cost of counting `total` + fetching a page vs table size `N` and **`limit`**, assuming an index on **`category`** (state assumptions).

## Part C — contract
Two bullets: what JSON change would **break** mobile clients, and how you version or document it.

Use the words **pagination**, **pytest**, **edge case**, and **complexity** in the prose.""",
            hints={
                "min_chars": 1300,
                "required_keywords": ["pagination", "pytest", "edge case", "complexity"],
                "bonus_keywords": ["422", "contract", "offset", "parametrize", "index"],
            },
            attribution="Synthesized from FastAPI testing guidance, MDN Big-O glossary, and common interview pagination prompts.",
        ),
    },
    # Day 12
    {
        "module": "platform",
        "day_index": 12,
        "slug": "d12-docker",
        "title": "Day 12 — Docker & containerization fundamentals",
        "summary": "Images, layers, ports, and reproducible dev environments.",
        "video_url": "https://www.youtube.com/embed/fqMOX6JJhGo",
        "key_concepts": ["image vs container", "Dockerfile layers", "multi-stage builds (concept)", "volumes"],
        "resources": [
            {"label": "Docker curriculum — containers intro", "url": "https://github.com/docker/labs/tree/master"},
            {"label": "Play with Docker classroom", "url": "https://training.play-with-docker.com/"},
        ],
        "learning_goals": ["Build a small image for a Python or Node service", "Explain cache invalidation in Dockerfiles"],
        "deliverables": ["Dockerfile + `docker run` notes"],
        "evaluation_rubric": [
            {"criterion": "Container correctness", "weight": 0.3},
            {"criterion": "Security basics (non-root, pins)", "weight": 0.25},
            {"criterion": "Explainability", "weight": 0.25},
            {"criterion": "DevEx", "weight": 0.2},
        ],
        "exercise_brief": "Containerize a hello API or static server. Document build and run.",
        "exercise": _ex(
            "dockerfile-production-review",
            "Review and improve a Dockerfile for production",
            """## Goal
Show you understand **docker** **image** vs **container**, **layer** caching, and production hardening.

## Paste
1. A sample `Dockerfile` in a fenced block (hello API or static site — your pick).
2. **Five** numbered improvements for production: base **image** pin, non-root user, **healthcheck**, env/config, slimming or multi-stage.
3. **Tradeoff:** one thing you deliberately keep simple and why.

Use the words **docker**, **image**, **container**, and **layer** in plain English too (not only in code).""",
            hints={
                "min_chars": 1150,
                "required_keywords": ["docker", "image", "container", "layer"],
                "bonus_keywords": ["healthcheck", "non-root", "multi-stage"],
                "expects_code_fence": True,
            },
            attribution="Draws from Docker official labs and Play with Docker style exercises.",
        ),
    },
    # Day 13
    {
        "module": "platform",
        "day_index": 13,
        "slug": "d13-kubernetes-basics",
        "title": "Day 13 — Kubernetes: pods, deployments, services, ConfigMaps",
        "summary": "Declare desired state; let the control plane converge.",
        "video_url": "https://www.youtube.com/embed/DCoBcpOA7W4",
        "key_concepts": ["Pod", "Deployment", "Service", "ConfigMap/Secret", "labels/selectors"],
        "resources": [
            {"label": "Kubernetes Course Labs", "url": "https://kubernetes.courselabs.co/"},
            {"label": "K8s concepts overview", "url": "https://kubernetes.io/docs/concepts/"},
        ],
        "learning_goals": ["Write minimal Deployment+Service YAML", "Explain rolling update benefits", "Wire env from ConfigMap"],
        "deliverables": ["YAML manifests + kubectl apply narrative"],
        "evaluation_rubric": [
            {"criterion": "Manifest correctness", "weight": 0.35},
            {"criterion": "Networking clarity", "weight": 0.25},
            {"criterion": "Config hygiene", "weight": 0.2},
            {"criterion": "Operational notes", "weight": 0.2},
        ],
        "exercise_brief": "Deploy a two-replica API with a ClusterIP service and externalized config.",
        "exercise": _ex(
            "kubernetes-deployment-service-configmap",
            "Write Kubernetes Deployment, Service, and ConfigMap YAML",
            """## Goal
Declare a minimal **deployment** + **service** + **configmap** so an API runs with externalized config.

## Paste
1. YAML in fenced blocks (can be partial but structurally valid): **Deployment**, **Service** (ClusterIP OK), **ConfigMap**.
2. For each resource, 2–3 bullets: what fields you set and why (labels, selectors, ports, envFrom, etc.).
3. **Scaling:** how you change replica count and what Kubernetes does (rolling idea).
4. **Failure:** what breaks if the **ConfigMap** key is missing or wrong — how a **pod** misbehaves.

Use **deployment**, **service**, **configmap**, and **pod** in the narrative.""",
            hints={
                "min_chars": 1500,
                "required_keywords": ["deployment", "service", "configmap", "pod"],
                "bonus_keywords": ["replica", "rolling", "probe"],
                "expects_code_fence": True,
            },
            attribution="Topics align with kubernetes.courselabs.co and core CKAD-style skills (without exam spoilers).",
        ),
    },
    # Day 14
    {
        "module": "platform",
        "day_index": 14,
        "slug": "d14-cicd-rancher",
        "title": "Day 14 — CI/CD mindset, GitOps touch, Rancher awareness",
        "summary": "Automate the boring path to production; know how clusters are managed.",
        "video_url": "https://www.youtube.com/embed/scEDHsr3APg",
        "key_concepts": ["pipeline stages", "artifact promotion", "secrets in CI", "Rancher as control plane"],
        "resources": [
            {"label": "GitHub Actions docs", "url": "https://docs.github.com/en/actions"},
            {"label": "Rancher docs — overview", "url": "https://ranchermanager.docs.rancher.com/"},
        ],
        "learning_goals": ["Sketch a pipeline for test→build→scan→deploy", "Identify secret handling mistakes"],
        "deliverables": ["Mermaid or bullet pipeline diagram"],
        "evaluation_rubric": [
            {"criterion": "Pipeline completeness", "weight": 0.3},
            {"criterion": "Security", "weight": 0.3},
            {"criterion": "Operational realism", "weight": 0.2},
            {"criterion": "Communication", "weight": 0.2},
        ],
        "exercise_brief": "Design CI for this monorepo: frontend + backend + docker publish.",
        "exercise": _ex(
            "monorepo-cicd-pipeline-design",
            "Design a CI/CD pipeline for frontend and backend",
            """## Goal
Sketch a **pipeline** that **test**s, builds, and **deploy**s this kind of monorepo without leaking **secret**s.

## Repo shape
`frontend/` (npm), `backend/` (Python), one Docker image per service (or explain your alternative).

## Paste — numbered sections
1. **Triggers:** PR vs main; path filters if any.
2. **Jobs:** install → lint/**test** → build → image publish → **deploy** hook.
3. **Secrets:** where API tokens live; what never hits logs.
4. **Rollback:** one concrete strategy (re-tag, helm rollback, manual kubectl, etc.).
5. Optional: when **Rancher** or another control plane fits (one sentence).

Use **pipeline**, **test**, **deploy**, and **secret** in prose.""",
            hints={
                "min_chars": 1500,
                "required_keywords": ["pipeline", "test", "deploy", "secret"],
                "bonus_keywords": ["github actions", "rollback", "rancher"],
            },
            attribution="Synthesized from GitHub Actions docs and common internal platform patterns.",
        ),
    },
    # Day 15
    {
        "module": "platform",
        "day_index": 15,
        "slug": "d15-system-design-capstone",
        "title": "Day 15 — System design capstone: URL shortener",
        "summary": "Communicate requirements, data flow, APIs, storage, and scaling tradeoffs.",
        "video_url": "https://www.youtube.com/embed/M576WGiKEdU",
        "key_concepts": ["requirements", "estimation", "API design", "storage schema", "caching", "tradeoffs"],
        "resources": [
            {"label": "System Design — URL shortener walkthrough", "url": "https://www.systemdesignhandbook.com/guides/design-a-url-shortening-service/"},
            {"label": "System Design School — URL shortener", "url": "https://systemdesignschool.io/problems/url-shortener/solution"},
        ],
        "learning_goals": [
            "Produce a structured design doc",
            "Discuss read-heavy patterns",
            "Identify single points of failure",
        ],
        "deliverables": ["Architecture diagram description + API outline + risk section"],
        "evaluation_rubric": [
            {"criterion": "Problem framing", "weight": 0.25},
            {"criterion": "Data model", "weight": 0.25},
            {"criterion": "Scalability", "weight": 0.25},
            {"criterion": "Production readiness", "weight": 0.25},
        ],
        "exercise_brief": "Design TinyURL-like service for 100:1 read/write with global latency goals.",
        "exercise": _ex(
            "url-shortener-system-design",
            "Design document: URL shortening service",
            """## Goal
Produce a readable design for a read-heavy URL shortener with clear **API**, **cache**, **scalab**ility story, and honest **tradeoff**s.

## Paste — use these headings
### Requirements
Functional + non-functional (latency, durability, abuse).

### **API**
Create short link, resolve **redirect**, analytics optional.

### Data model
Tables/keys; how you avoid **collision**s.

### ID generation
**Base62** or other scheme; security of guessable IDs.

### **Cache** & read path
What is cached; TTL; invalidation sketch.

### Failure & monitoring
**Availability** risks; metrics/alerts.

### Capacity
Rough QPS/storage napkin math (order-of-magnitude).

Use **api**, **scalab** (e.g. scalable/scalability), **cache**, and **tradeoff** in the text.""",
            hints={
                "min_chars": 1500,
                "required_keywords": ["api", "scalab", "cache", "tradeoff"],
                "bonus_keywords": ["redirect", "collision", "base62", "availability"],
            },
            attribution="Classic URL shortener prompt as used across System Design Handbook and System Design School.",
        ),
    },
]


# Module-tied vocabulary for extra drills (must appear in student text for auto-grade).
_MODULE_DRILL_QUARTET: dict[str, tuple[str, str, str, str]] = {
    "foundations": ("command", "shell", "branch", "commit"),
    "frontend": ("component", "state", "props", "render"),
    "backend": ("endpoint", "validation", "schema", "request"),
    "platform": ("container", "deploy", "pipeline", "cluster"),
}


def _four_follow_on_drills(slug_base: str, title_short: str, module: str) -> list[dict[str, Any]]:
    t = _MODULE_DRILL_QUARTET.get(module, ("system", "change", "risk", "verify"))
    w1, w2, w3, w4 = t
    return [
        _ex(
            f"{slug_base}-drill-checklist",
            f"Checklist: what to remember from {title_short}",
            (
                f"## Goal\nSolidify **{title_short}** as something you can recall under stress.\n\n"
                "## Paste\n"
                "- **8–12** bullet **checklist** items you would keep on a personal cheat sheet.\n"
                "- Each bullet is one line; no long paragraphs.\n"
                "- At least **two** bullets must name a concrete **tool**, **command**, **API**, or **object** from this topic.\n\n"
                f"Use the words **checklist**, **remember**, **{w1}**, and **{w2}** in the prose (not only in headings)."
            ),
            difficulty="medium",
            hints={
                "min_chars": 720,
                "required_keywords": ["checklist", "remember", w1, w2],
                "bonus_keywords": ["gotcha", "syntax", "example"],
            },
            attribution="Automat Washing — retention drill.",
            sort_order=2,
        ),
        _ex(
            f"{slug_base}-drill-tradeoff",
            f"Decision memo: two approaches for {title_short}",
            (
                f"## Scenario\nChoose between **approach** A and **approach** B for one real decision in **{title_short}**.\n\n"
                "## Paste — sections\n"
                "### Context\nOne paragraph: what decision you are facing.\n\n"
                "### Option A\nWhat it wins, what it costs.\n\n"
                "### Option B\nWhat it wins, what it costs.\n\n"
                "### Pick\nWhich you choose **when** and why.\n\n"
                "### **Risk**\nMain **risk** if you are wrong.\n\n"
                "Use **tradeoff**, **approach**, **when**, and **risk** in the body."
            ),
            difficulty="medium",
            hints={
                "min_chars": 880,
                "required_keywords": ["tradeoff", "approach", "when", "risk"],
                "bonus_keywords": ["rollback", "constraint", w3],
            },
            attribution="Automat Washing — decision drill.",
            sort_order=3,
        ),
        _ex(
            f"{slug_base}-drill-procedure",
            f"Procedure: numbered walkthrough for {title_short}",
            (
                f"## Goal\nProve you can execute a slice of **{title_short}** as a repeatable **procedure**.\n\n"
                "## Paste\n"
                "- **At least 8** numbered **step**s (what to run, click, or type).\n"
                "- A **verify** section: what you look at to know it worked (**outcome**).\n"
                "- One sentence on what you would **automate** next.\n\n"
                f"Include **step**, **verify**, **outcome**, and **{w3}** in the text."
            ),
            difficulty="medium",
            hints={
                "min_chars": 800,
                "required_keywords": ["step", "verify", "outcome", w3],
                "bonus_keywords": ["script", "log", "dashboard"],
            },
            attribution="Automat Washing — runbook drill.",
            sort_order=4,
        ),
        _ex(
            f"{slug_base}-drill-review-snippet",
            f"Review: find defects in a snippet for {title_short}",
            (
                f"## Goal\nPractice review skills on **{title_short}**.\n\n"
                "## Invent\n"
                "Write a short **wrong** or fragile **snippet** (10–25 lines) in a ``` fenced block: shell, TypeScript, Python, YAML, or Dockerfile — tied to this day.\n\n"
                "## Paste\n"
                "- Label **three** **defect**s (line references or short quotes).\n"
                "- For each **defect**, one paragraph **fix**: what you change and why.\n"
                "- Close with one **test** or **check** you add so it cannot regress.\n\n"
                "Use **defect**, **fix**, **snippet**, and **test** in the narrative."
            ),
            difficulty="hard",
            hints={
                "min_chars": 900,
                "required_keywords": ["defect", "fix", "snippet", "test"],
                "bonus_keywords": ["lint", "review", w4],
                "expects_code_fence": True,
            },
            attribution="Automat Washing — review drill.",
            sort_order=5,
        ),
    ]


def enrich_bootcamp_days(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Schedule blocks, resources, and six graded exercises per day (main + Part 2 + four drills)."""
    out: list[dict[str, Any]] = []
    for d in raw:
        main_ex = d["exercise"]
        slug_base = main_ex["slug"]
        day_index = d["day_index"]
        title_short = d["title"].split("—", 1)[-1].strip() if "—" in d["title"] else d["title"]

        schedule_block = {
            "label": f"Suggested ~12h schedule — Day {day_index}",
            "url": "#day-schedule",
            "blocks": [
                {
                    "hours": 1.25,
                    "title": "Video + structured notes",
                    "detail": "Watch the embed; note ideas you will reuse across all six written submissions.",
                },
                {
                    "hours": 1.5,
                    "title": "Reading + cheat sheet",
                    "detail": "Work through linked docs; half-page cheat sheet of commands, APIs, or patterns.",
                },
                {
                    "hours": 2.0,
                    "title": "Exercise 1 — main topic + submit",
                    "detail": "Full-length answer; match required keywords before submit.",
                },
                {
                    "hours": 2.0,
                    "title": "Exercise 2 — Part 2 (extended) + submit",
                    "detail": "Failure modes, numbers, mitigations, two fenced snippets.",
                },
                {
                    "hours": 1.25,
                    "title": "Exercise 3 — checklist drill + submit",
                    "detail": "Retention checklist for this day’s theme.",
                },
                {
                    "hours": 1.25,
                    "title": "Exercise 4 — tradeoff memo + submit",
                    "detail": "Two approaches, pick, and state risks.",
                },
                {
                    "hours": 1.25,
                    "title": "Exercise 5 — procedure + submit",
                    "detail": "Numbered steps plus how you verify the outcome.",
                },
                {
                    "hours": 1.25,
                    "title": "Exercise 6 — snippet review + submit",
                    "detail": "Invent a flawed snippet; list defects, fixes, and a regression check.",
                },
            ],
        }
        orig_resources = list(d.get("resources", []))
        embed, watch, vid_note = PRIMARY_VIDEOS[day_index]
        video_resource: dict[str, Any] = {
            "label": "Primary YouTube tutorial (watch on YouTube)",
            "url": watch,
            "note": vid_note,
        }
        resources = [schedule_block, video_resource, *orig_resources]
        learning_goals = [
            "Budget ~12 focused engineer-hours for this day (see schedule).",
            *list(d.get("learning_goals", [])),
        ]
        deliverables = [
            *list(d.get("deliverables", [])),
            "Six separate graded submissions today (main, Part 2, checklist, tradeoff, procedure, snippet review).",
        ]
        key_concepts = [
            *list(d.get("key_concepts", [])),
            "Assume bad input, partial outages, and abusive traffic — design and test for that.",
            "Quantify: back-of-envelope capacity, latency, or cost before you argue for a design.",
        ]

        part_two = _ex(
            f"{slug_base}-part-two",
            "Part 2: harder follow-on (submit after Part 1)",
            (
                f"## Separate graded submission\n"
                f"Complete **Part 1** first. This **Part 2** stands alone: deeper stress on **{title_short}**.\n\n"
                "## A — Two failure scenarios\n"
                "Describe **two** different **failure** modes (abuse, overload, misconfig, dependency down, bad deploy, etc.). "
                "For each: what triggers it, user-visible symptom, what you **measure** in **production**, first **mitigation**.\n\n"
                "## B — One number\n"
                "Pick **one** concrete **measure**: p95 latency, max RPS, rows scanned, pods, cost per 1k requests, etc. "
                "Show a napkin estimate **or** how you would benchmark/measure it (tool + metric name).\n\n"
                "## C — Five mitigations\n"
                "List **five** specific hardening steps tied to this topic (config, code change, alert, runbook line, **test** case). "
                "At least **two** must be automated **test**s, checks in CI, or assertions — not prose alone.\n\n"
                "## D — Two snippets\n"
                "Paste **two** separate ``` fenced blocks (code, config, policy, or **test**). They must differ in kind "
                "(e.g. **test** + shell, YAML + Python).\n\n"
                "## Bar\n"
                "No generic advice. Every paragraph should be actionable for this day’s topic."
            ),
            difficulty="hard",
            hints={
                "min_chars": 1600,
                "required_keywords": ["failure", "measure", "mitigation", "test", "production"],
                "bonus_keywords": ["benchmark", "latency", "alert", "rollback", "load", "capacity"],
                "expects_code_fence": True,
            },
            attribution="Automat Washing — extended scenario lab.",
            sort_order=1,
        )
        main_adj = {**main_ex, "sort_order": 0}
        mod = str(d.get("module", "backend"))
        extra = _four_follow_on_drills(slug_base, title_short, mod)
        base = {k: v for k, v in d.items() if k != "exercise"}
        out.append(
            {
                **base,
                "video_url": embed,
                "resources": resources,
                "learning_goals": learning_goals,
                "deliverables": deliverables,
                "key_concepts": key_concepts,
                "exercises": [main_adj, part_two, *extra],
            }
        )
    return out


DAYS: list[dict[str, Any]] = enrich_bootcamp_days(_RAW_DAYS)
