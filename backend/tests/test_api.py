def auth_headers(client) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={"email": "api@example.com", "password": "StrongPassword123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": "api@example.com", "password": "StrongPassword123"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_get_client(client) -> None:
    headers = auth_headers(client)
    response = client.post("/api/v1/clients", json={"name": "Pessoa Teste"}, headers=headers)
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Pessoa Teste"
    assert created["id"] == 1

    response = client.get("/api/v1/clients/1", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Pessoa Teste"


def test_list_clients(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Um"}, headers=headers)

    response = client.get("/api/v1/clients", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_user_can_only_create_one_client_profile(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Um"}, headers=headers)

    response = client.post("/api/v1/clients", json={"name": "Dois"}, headers=headers)
    assert response.status_code == 409


def test_update_client(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Antigo"}, headers=headers)

    response = client.patch("/api/v1/clients/1", json={"name": "Novo"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Novo"


def test_delete_client(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Apagar"}, headers=headers)

    response = client.delete("/api/v1/clients/1", headers=headers)
    assert response.status_code == 204

    response = client.get("/api/v1/clients/1", headers=headers)
    assert response.status_code == 404


def test_get_client_not_found(client) -> None:
    headers = auth_headers(client)
    response = client.get("/api/v1/clients/999", headers=headers)
    assert response.status_code == 404


def test_create_goal_for_client(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Com Objetivo"}, headers=headers)
    response = client.post(
        "/api/v1/clients/1/goal",
        json={"description": "Manter peso"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["description"] == "Manter peso"
    assert response.json()["client_id"] == 1


def test_create_diet_for_client(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Com Dieta"}, headers=headers)
    response = client.post(
        "/api/v1/clients/1/diet",
        json={"description": "Dieta balanceada"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["description"] == "Dieta balanceada"


def test_create_meal_for_client(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Com Refeição"}, headers=headers)
    response = client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01", "image_url": "almoco.jpg"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["meal_date"] == "2026-01-01"
    assert response.json()["image_url"] == "almoco.jpg"


def test_get_client_with_relations(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Completo"}, headers=headers)
    client.post("/api/v1/clients/1/goal", json={"description": "Perder peso"}, headers=headers)
    client.post("/api/v1/clients/1/diet", json={"description": "Dieta low carb"}, headers=headers)
    client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01"},
        headers=headers,
    )

    response = client.get("/api/v1/clients/1/full", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["goal"]["description"] == "Perder peso"
    assert data["diet"]["description"] == "Dieta low carb"
    assert len(data["meals"]) == 1


def test_create_meal_invalid_client(client) -> None:
    headers = auth_headers(client)
    response = client.post(
        "/api/v1/clients/999/meal",
        json={"meal_date": "2026-01-01"},
        headers=headers,
    )
    assert response.status_code == 404


def test_client_endpoints_require_authentication(client) -> None:
    response = client.get("/api/v1/clients")
    assert response.status_code == 401


def test_users_cannot_access_each_others_clients(client) -> None:
    owner_headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Privado"}, headers=owner_headers)

    client.post(
        "/api/v1/auth/register",
        json={"email": "other@example.com", "password": "StrongPassword123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": "other@example.com", "password": "StrongPassword123"},
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/clients/1", headers=other_headers)
    assert response.status_code == 404

    response = client.get("/api/v1/clients", headers=other_headers)
    assert response.status_code == 200
    assert response.json() == []
