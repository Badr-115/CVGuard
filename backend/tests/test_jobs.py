def auth(client, email="owner@example.com"):
    r = client.post("/api/v1/auth/register", json={
        "organization_name": "Acme",
        "email": email,
        "password": "StrongPassword123!",
    })
    assert r.status_code == 201
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_create_and_list_job(client):
    headers = auth(client)
    r = client.post("/api/v1/jobs", headers=headers, json={
        "title": "Backend Engineer",
        "description": "Build Python services with PostgreSQL and Docker.",
        "required_skills": ["Python", "PostgreSQL", "Docker"],
    })
    assert r.status_code == 201
    assert r.json()["required_skills"] == ["Python", "PostgreSQL", "Docker"]

    listed = client.get("/api/v1/jobs", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_tenant_isolation(client):
    owner_headers = auth(client, "a@example.com")
    client.post("/api/v1/jobs", headers=owner_headers, json={
        "title": "Private Role",
        "description": "Internal role for Python engineers.",
        "required_skills": ["Python"],
    })
    other_headers = auth(client, "b@example.com")
    listed = client.get("/api/v1/jobs", headers=other_headers)
    assert listed.status_code == 200
    assert listed.json() == []
