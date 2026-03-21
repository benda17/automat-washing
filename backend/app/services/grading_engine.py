"""
Automatic submission review: rubric-weighted heuristic scoring with structured narrative feedback.
Complements human review; teachers can override via manual review API.
"""

from __future__ import annotations

import re
from typing import Any

DEFAULT_WEIGHTS: dict[str, float] = {
    "correctness": 0.14,
    "code_quality": 0.10,
    "naming": 0.06,
    "architecture": 0.08,
    "readability": 0.10,
    "git_hygiene": 0.06,
    "documentation": 0.08,
    "complexity_awareness": 0.08,
    "best_practices": 0.10,
    "edge_cases": 0.06,
    "testing_effort": 0.08,
    "maintainability": 0.06,
}


def _clamp(n: int) -> int:
    return max(0, min(100, n))


def _normalize_weights(custom: dict[str, float] | None) -> dict[str, float]:
    base = dict(DEFAULT_WEIGHTS)
    if custom:
        base.update({k: float(v) for k, v in custom.items() if k in DEFAULT_WEIGHTS})
    s = sum(base.values()) or 1.0
    return {k: v / s for k, v in base.items()}


def evaluate_submission(
    content: str,
    *,
    exercise_title: str,
    auto_eval_hints: dict[str, Any] | None,
    rubric_weights: dict[str, float] | None,
) -> dict[str, Any]:
    hints = auto_eval_hints or {}
    text = content.strip()
    lower = text.lower()
    weights = _normalize_weights(rubric_weights)

    min_len = int(hints.get("min_chars", 400))
    required_keywords = [str(k).lower() for k in hints.get("required_keywords", [])]
    bonus_keywords = [str(k).lower() for k in hints.get("bonus_keywords", [])]
    anti_patterns = [str(k).lower() for k in hints.get("anti_patterns", [])]

    # --- dimension heuristics (0–100) ---
    length_score = _clamp(55 + min(45, (len(text) - min_len) // 15)) if len(text) >= min_len else _clamp(len(text) * 100 // max(min_len, 1))

    missing_required = [k for k in required_keywords if k not in lower]
    keyword_coverage = 100 - min(100, len(missing_required) * 12)

    bonus_hits = sum(1 for k in bonus_keywords if k in lower)
    bonus = min(25, bonus_hits * 5)

    anti_hits = sum(1 for a in anti_patterns if a in lower)
    penalty = min(40, anti_hits * 15)

    has_headers = bool(re.search(r"^#{1,3}\s+\S+", text, re.MULTILINE))
    has_list = bool(re.search(r"^[-*]\s+\S+", text, re.MULTILINE)) or bool(re.search(r"^\d+\.\s+\S+", text, re.MULTILINE))
    has_code_fence = "```" in text
    structure_score = _clamp(40 + (15 if has_headers else 0) + (15 if has_list else 0) + (20 if has_code_fence else 0))

    mentions_test = any(x in lower for x in ("test", "pytest", "jest", "unit test", "coverage"))
    mentions_error = any(x in lower for x in ("error", "exception", "validation", "422", "try", "except"))
    mentions_complexity = any(x in lower for x in ("o(", "complexity", "big o", "scalab", "bottleneck", "tradeoff", "trade-off"))
    mentions_git = any(x in lower for x in ("branch", "commit", "pull request", "pr", "rebase", "merge", "diff"))
    mentions_docs = any(x in lower for x in ("readme", "docstring", "openapi", "swagger", "comment", "adr"))

    correctness = _clamp(int(keyword_coverage * 0.7 + length_score * 0.3) + bonus // 4 - penalty // 2)
    code_quality = _clamp(structure_score + (10 if has_code_fence else -5) + (5 if mentions_error else 0))
    naming = _clamp(60 + (10 if "naming" in lower or "variable" in lower else 0) + (10 if has_list else 0))
    architecture = _clamp(55 + (15 if any(x in lower for x in ("layer", "module", "router", "service", "boundary")) else 0))
    readability = _clamp(structure_score + (10 if has_headers else 0))
    git_hygiene = _clamp(50 + (25 if mentions_git else 0) + (10 if "conventional" in lower or "message" in lower else 0))
    documentation = _clamp(55 + (20 if mentions_docs else 0) + (10 if has_headers else 0))
    complexity_awareness = _clamp(50 + (30 if mentions_complexity else 0) + (10 if "edge" in lower or "boundary" in lower else 0))
    best_practices = _clamp(52 + bonus - anti_hits * 8)
    edge_cases = _clamp(50 + (25 if any(x in lower for x in ("edge case", "empty", "null", "timeout", "race")) else 0))
    testing_effort = _clamp(48 + (30 if mentions_test else 0) + (10 if "e2e" in lower or "integration" in lower else 0))
    maintainability = _clamp((readability + documentation + naming) // 3)

    dimensions: dict[str, int] = {
        "correctness": correctness,
        "code_quality": code_quality,
        "naming": naming,
        "architecture": architecture,
        "readability": readability,
        "git_hygiene": git_hygiene,
        "documentation": documentation,
        "complexity_awareness": complexity_awareness,
        "best_practices": best_practices,
        "edge_cases": edge_cases,
        "testing_effort": testing_effort,
        "maintainability": maintainability,
    }

    overall = int(round(sum(dimensions[k] * weights[k] for k in dimensions)))

    strengths: list[str] = []
    weaknesses: list[str] = []
    improvements: list[str] = []

    if len(text) >= min_len:
        strengths.append("Submission meets minimum depth for a serious engineering write-up.")
    else:
        weaknesses.append(f"Response is shorter than the expected ~{min_len} characters for this prompt.")
        improvements.append("Expand with concrete examples, steps you took, and what you would change next iteration.")

    if not missing_required:
        strengths.append("Covers the core concepts the prompt asked for.")
    else:
        weaknesses.append(f"Missing expected themes: {', '.join(missing_required[:6])}{'…' if len(missing_required) > 6 else ''}.")
        improvements.append("Re-read the brief and explicitly address each required concept with a short paragraph or bullet.")

    if has_headers and has_list:
        strengths.append("Good information architecture: headings and lists make your reasoning scannable.")
    elif not has_headers:
        improvements.append("Add Markdown headings (##) to separate context, approach, tradeoffs, and verification.")

    if has_code_fence:
        strengths.append("Includes code or config snippets — that anchors the review in something concrete.")
    elif "code" in exercise_title.lower() or hints.get("expects_code_fence"):
        improvements.append("Where relevant, paste a small code/config excerpt and narrate the decisions around it.")

    if mentions_test:
        strengths.append("You connected work to testing — that is how we ship confidently.")
    else:
        weaknesses.append("Limited discussion of how you would test or validate the solution.")
        improvements.append("Add a short test plan: unit cases, API contract checks, or manual scenarios.")

    if mentions_complexity:
        strengths.append("Shows awareness of performance/scalability tradeoffs.")
    else:
        improvements.append("Call out complexity, bottlenecks, or caching assumptions — even rough Big-O is valuable.")

    if mentions_git:
        strengths.append("Touches collaboration hygiene (branches, PRs, commits) — keep that habit.")
    else:
        improvements.append("Describe the git/PR workflow you would use for this change (branch name, commit granularity, review).")

    if anti_hits:
        weaknesses.append("Some phrases read like anti-patterns for production code; tighten assumptions and safety.")

    strong_lines = [f"- {s}" for s in strengths[:5]] or ["- (No strong signals detected; deepen the narrative.)"]
    weak_lines = [f"- {w}" for w in weaknesses[:5]] or [
        "- Looks good directionally; still add risks, tests, and tradeoffs."
    ]
    next_lines = [f"- {i}" for i in improvements[:6]]

    feedback_parts = [
        f"## Auto review — {exercise_title}",
        "",
        f"**Auto-score:** {overall}/100 (heuristic; not a substitute for human judgment on correctness).",
        "",
        "### What reads strong",
        *strong_lines,
        "",
        "### What to tighten",
        *weak_lines,
        "",
        "### Next actions",
        *next_lines,
        "",
        "### Dimension snapshot",
        "\n".join(f"- **{k.replace('_', ' ')}:** {v}/100" for k, v in sorted(dimensions.items())),
    ]
    feedback = "\n".join(feedback_parts)

    mentor_tone = (
        "Automated review emphasizes clear structure, explicit reasoning, and operational awareness. "
        "If a dimension scores low, add evidence: commands, diagrams, tests, or concrete examples."
    )

    return {
        "overall_score": _clamp(overall),
        "dimension_scores": dimensions,
        "feedback": feedback,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "improvements": improvements,
        "mentor_tone_notes": mentor_tone,
    }
