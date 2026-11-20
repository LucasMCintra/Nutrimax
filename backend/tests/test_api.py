
def test_create_and_get_client(client) -> None:
    response = client.post("/api/v1/clients", json={"name": "Pessoa Teste"})
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Pessoa Teste"
    assert created["id"] == 1

    response = client.get("/api/v1/clients/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Pessoa Teste"


def test_list_clients(client) -> None:
    client.post("/api/v1/clients", json={"name": "Um"})
    client.post("/api/v1/clients", json={"name": "Dois"})

    response = client.get("/api/v1/clients")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_client(client) -> None:
    client.post("/api/v1/clients", json={"name": "Antigo"})

    response = client.patch("/api/v1/clients/1", json={"name": "Novo"})
    assert response.status_code == 200
    assert response.json()["name"] == "Novo"


def test_delete_client(client) -> None:
    client.post("/api/v1/clients", json={"name": "Apagar"})

    response = client.delete("/api/v1/clients/1")
    assert response.status_code == 204

    response = client.get("/api/v1/clients/1")
    assert response.status_code == 404


def test_get_client_not_found(client) -> None:
    response = client.get("/api/v1/clients/999")
    assert response.status_code == 404


def test_create_goal_for_client(client) -> None:
    client.post("/api/v1/clients", json={"name": "Com Objetivo"})
    response = client.post(
        "/api/v1/clients/1/goal",
        json={"description": "Manter peso"},
    )
    assert response.status_code == 201
    assert response.json()["description"] == "Manter peso"
    assert response.json()["client_id"] == 1


def test_create_diet_for_client(client) -> None:
    client.post("/api/v1/clients", json={"name": "Com Dieta"})
    response = client.post(
        "/api/v1/clients/1/diet",
        json={"description": "Dieta balanceada"},
    )
    assert response.status_code == 201
    assert response.json()["description"] == "Dieta balanceada"


def test_create_meal_for_client(client) -> None:
    client.post("/api/v1/clients", json={"name": "Com Refeição"})
    response = client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01", "image_url": "almoco.jpg"},
    )
    assert response.status_code == 201
    assert response.json()["meal_date"] == "2026-01-01"
    assert response.json()["image_url"] == "almoco.jpg"


def test_get_client_with_relations(client) -> None:
    client.post("/api/v1/clients", json={"name": "Completo"})
    client.post("/api/v1/clients/1/goal", json={"description": "Perder peso"})
    client.post("/api/v1/clients/1/diet", json={"description": "Dieta low carb"})
    client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01"},
    )

    response = client.get("/api/v1/clients/1/full")
    assert response.status_code == 200
    data = response.json()
    assert data["goal"]["description"] == "Perder peso"
    assert data["diet"]["description"] == "Dieta low carb"
    assert len(data["meals"]) == 1


def test_create_meal_invalid_client(client) -> None:
    response = client.post(
        "/api/v1/clients/999/meal",
        json={"meal_date": "2026-01-01"},
    )
    assert response.status_code == 404


def test_health_check(client) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}