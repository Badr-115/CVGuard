from app.services.scoring import explain_score, score_candidate


def test_phrase_skills_and_missing_skills_are_explainable():
    result = explain_score(
        "Python developer with machine learning and PostgreSQL experience",
        ["Python", "Machine Learning", "Docker"],
        "Build data services with Python and PostgreSQL.",
    )
    assert result["matched_skills"] == ["Python", "Machine Learning"]
    assert result["missing_skills"] == ["Docker"]
    assert 50 <= result["score"] <= 100


def test_empty_resume_is_zero():
    assert score_candidate("", ["Python"], "Python backend role") == 0.0
