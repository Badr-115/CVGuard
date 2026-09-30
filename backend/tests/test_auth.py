def test_register_and_me(client):
    r = client.post("/api/v1/auth/register", json={
        "organization_name": "Acme",
        "email": "owner@example.com",
        "password": "StrongPassword123!"
    })
    assert r.status_code == 201
    token = r.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "OWNER"
