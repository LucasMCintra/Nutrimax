def test_register_login_and_current_user(client) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "StrongPassword123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"
    assert "password_hash" not in response.json()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "StrongPassword123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


def test_duplicate_email_and_invalid_login(client) -> None:
    payload = {"email": "duplicate@example.com", "password": "StrongPassword123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409

    response = client.post(
        "/api/v1/auth/login",
        data={"username": payload["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_current_user_requires_token(client) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
