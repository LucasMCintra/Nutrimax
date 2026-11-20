def auth_headers(client) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={"email": "dashboard@example.com", "password": "StrongPassword123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": "dashboard@example.com", "password": "StrongPassword123"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_target_and_summary(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Dashboard"}, headers=headers)
    target = {
        "calories": 2000,
        "protein": 150,
        "carbohydrates": 220,
        "fat": 60,
    }

    response = client.put("/api/v1/dashboard/target", json=target, headers=headers)
    assert response.status_code == 200
    assert response.json()["calories"] == 2000

    client.post(
        "/api/v1/clients/1/meal",
        json={
            "meal_date": "2026-11-20",
            "calories": 650,
            "protein": 40,
            "carbohydrates": 70,
            "fat": 20,
        },
        headers=headers,
    )
    response = client.get(
        "/api/v1/dashboard/summary?reference_date=2026-11-20", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["day"]["calories"] == 650
    assert response.json()["week"]["protein"] == 40
    assert response.json()["month"]["fat"] == 20


def test_dashboard_isolated_without_client(client) -> None:
    headers = auth_headers(client)
    response = client.get("/api/v1/dashboard/summary", headers=headers)
    assert response.status_code == 404
