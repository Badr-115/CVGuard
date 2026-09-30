"""Explainable resume/job fit scoring.

This is a deterministic matching aid, not a substitute for recruiter review.
It rewards explicit required-skill mentions and relevant job-description terms
while keeping the calculation bounded and inspectable.
"""

import re

_WORD_RE = re.compile(r"[\w+#./-]{2,}", re.UNICODE)
_STOPWORDS = {
    "and", "the", "with", "for", "from", "that", "this", "have", "has", "are",
    "you", "your", "our", "will", "into", "using", "use", "build", "building",
    "maintain", "maintaining", "work", "working", "years", "year", "role", "team",
}


def normalize(text: str) -> set[str]:
    return {token.casefold() for token in _WORD_RE.findall(text or "")}


def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").casefold()).strip()


def _skill_match(resume: str, skill: str) -> bool:
    normalized_skill = _compact(skill)
    if not normalized_skill:
        return False
    # Phrase matching avoids splitting "machine learning" into two unrelated hits.
    if " " in normalized_skill:
        return normalized_skill in _compact(resume)
    return normalized_skill in normalize(resume)


def score_candidate(resume_text: str, required_skills: list[str], description: str) -> float:
    if not resume_text.strip() or not required_skills:
        return 0.0

    skills = [skill.strip() for skill in required_skills if skill.strip()]
    matched = sum(_skill_match(resume_text, skill) for skill in skills)
    skill_score = matched / len(skills)

    resume_terms = normalize(resume_text)
    description_terms = {x for x in normalize(description) if x not in _STOPWORDS}
    context_hits = len(resume_terms & description_terms)
    context_score = min(1.0, context_hits / max(1, min(15, len(description_terms))))

    return round(min(100.0, skill_score * 80 + context_score * 20), 2)


def explain_score(resume_text: str, required_skills: list[str], description: str) -> dict:
    skills = [skill.strip() for skill in required_skills if skill.strip()]
    matched = [skill for skill in skills if _skill_match(resume_text, skill)]
    missing = [skill for skill in skills if skill not in matched]
    score = score_candidate(resume_text, skills, description)
    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "method": "deterministic_skill_and_context_match",
    }
