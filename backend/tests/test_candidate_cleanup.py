from pathlib import Path

import pytest

from app.api.v1 import candidates as candidates_module


def test_candidate_upload_is_removed_if_scoring_fails(client, monkeypatch, tmp_path):
    response = client.post("/api/v1/auth/register", json={
        "organization_name": "Example",
        "email": "owner@example.com",
        "password": "StrongPassword123!",
    })
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    job = client.post("/api/v1/jobs", headers=headers, json={
        "title": "Developer",
        "description": "Build Python APIs",
        "required_skills": ["Python"],
    })
    assert job.status_code == 201

    stored_file = Path(tmp_path) / "saved-resume.pdf"

    async def fake_save_resume(_upload):
        stored_file.write_bytes(b"temporary")
        return str(stored_file), "Python developer"

    def fail_score(*_args, **_kwargs):
        raise RuntimeError("forced scoring error")

    monkeypatch.setattr(candidates_module, "save_resume", fake_save_resume)
    monkeypatch.setattr(candidates_module, "explain_score", fail_score)

    with pytest.raises(RuntimeError, match="forced scoring error"):
        client.post(
            "/api/v1/candidates",
            headers=headers,
            data={"name": "Sample Candidate", "email": "candidate@example.com",
                  "job_id": str(job.json()["id"])},
            files={"resume": ("resume.pdf", b"pdf sample", "application/pdf")},
        )
    assert not stored_file.exists()
