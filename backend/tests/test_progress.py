def auth_headers(client) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={"email": "progress@example.com", "password": "StrongPassword123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": "progress@example.com", "password": "StrongPassword123"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_list_meals_and_progress(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Progress"}, headers=headers)
    client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-11-20", "calories": 500, "protein": 30},
        headers=headers,
    )
    client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-11-22", "calories": 700, "fat": 25},
        headers=headers,
    )

    response = client.get("/api/v1/clients/1/meals", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(
        "/api/v1/progress?start_date=2026-11-20&end_date=2026-11-22",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["points"]) == 3
    assert data["points"][0]["calories"] == 500
    assert data["points"][1]["calories"] == 0
    assert data["points"][2]["fat"] == 25


def test_progress_rejects_invalid_range(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Progress"}, headers=headers)
    response = client.get(
        "/api/v1/progress?start_date=2026-11-22&end_date=2026-11-20",
        headers=headers,
    )
    assert response.status_code == 422
