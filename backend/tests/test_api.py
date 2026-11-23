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


def test_update_goal_for_client(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Plano editável"}, headers=headers)

    response = client.put(
        "/api/v1/clients/1/goal",
        json={"description": "Ganhar massa muscular"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Ganhar massa muscular"
    assert response.json()["client_id"] == 1

    response = client.get("/api/v1/clients/1/full", headers=headers)
    assert response.json()["goal"]["description"] == "Ganhar massa muscular"


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


def test_run_meal_analysis_marks_provider_and_completed(client, monkeypatch) -> None:
    from app.ai_provider import GoogleAIStudioProvider
    from app.schemas import MealAnalysisItemBase

    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Análise Google"}, headers=headers)
    meal = client.post(
        "/api/v1/clients/1/meal", json={"meal_date": "2026-01-01"}, headers=headers
    ).json()
    image_path = client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/image",
        files={"image": ("meal.jpg", b"image", "image/jpeg")},
        headers=headers,
    )
    assert image_path.status_code == 200
    analysis = client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/analysis", headers=headers
    ).json()

    monkeypatch.setattr(
        GoogleAIStudioProvider,
        "analyze_meal",
        lambda self, image: [MealAnalysisItemBase(
            food_name="Salada",
            quantity=100,
            unit="g",
            calories=35,
            protein=2,
            carbohydrates=5,
            fat=1,
            confidence=0.88,
        )],
    )
    response = client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/analysis/{analysis['id']}/run",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["provider"] == "google_ai_studio"


def test_run_meal_analysis_marks_failed_without_image(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Análise sem imagem"}, headers=headers)
    meal = client.post(
        "/api/v1/clients/1/meal", json={"meal_date": "2026-01-01"}, headers=headers
    ).json()
    analysis = client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/analysis", headers=headers
    ).json()

    response = client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/analysis/{analysis['id']}/run",
        headers=headers,
    )
    assert response.status_code == 422
    response = client.get(f"/api/v1/clients/1/meals", headers=headers)
    assert response.status_code == 200


def test_meal_analysis_requires_confirmation_before_applying_items(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Análise"}, headers=headers)
    meal = client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01"},
        headers=headers,
    ).json()

    response = client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/analysis", headers=headers
    )
    assert response.status_code == 201
    analysis_id = response.json()["id"]
    assert response.json()["status"] == "pending"
    assert response.json()["provider"] == "manual"

    candidate = {
        "food_name": "Frango grelhado",
        "quantity": 120,
        "unit": "g",
        "calories": 198,
        "protein": 37,
        "carbohydrates": 0,
        "fat": 4,
        "confidence": 0.96,
    }
    response = client.put(
        f"/api/v1/clients/1/meal/{meal['id']}/analysis/{analysis_id}",
        json=[candidate],
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["items"][0]["food_name"] == "Frango grelhado"

    before_confirm = client.get("/api/v1/clients/1/meals", headers=headers).json()[0]
    assert before_confirm["calories"] == 0
    assert before_confirm["items"] == []

    response = client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/analysis/{analysis_id}/confirm",
        json={"item_ids": []},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["calories"] == 198
    assert response.json()["items"][0]["food_name"] == "Frango grelhado"
    assert response.json()["analyses"][0]["status"] == "confirmed"


def test_users_cannot_access_each_others_meal_analysis(client) -> None:
    owner_headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Análise privada"}, headers=owner_headers)
    meal = client.post(
        "/api/v1/clients/1/meal", json={"meal_date": "2026-01-01"}, headers=owner_headers
    ).json()
    analysis = client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/analysis", headers=owner_headers
    ).json()
    client.post(
        "/api/v1/auth/register",
        json={"email": "analysis-other@example.com", "password": "StrongPassword123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": "analysis-other@example.com", "password": "StrongPassword123"},
    ).json()["access_token"]
    response = client.put(
        f"/api/v1/clients/1/meal/{meal['id']}/analysis/{analysis['id']}",
        json=[],
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_meal_items_recalculate_meal_totals(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Itens"}, headers=headers)
    meal = client.post(
        "/api/v1/clients/1/meal", json={"meal_date": "2026-01-01"}, headers=headers
    ).json()
    item = {
        "food_name": "Arroz integral",
        "quantity": 150,
        "unit": "g",
        "calories": 180,
        "protein": 4,
        "carbohydrates": 38,
        "fat": 1,
    }
    response = client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/items", json=item, headers=headers
    )
    assert response.status_code == 201
    item_id = response.json()["id"]
    response = client.get(f"/api/v1/clients/1/meals", headers=headers)
    assert response.json()[0]["calories"] == 180
    assert response.json()[0]["items"][0]["food_name"] == "Arroz integral"

    response = client.put(
        f"/api/v1/clients/1/meal/{meal['id']}/items/{item_id}",
        json={**item, "calories": 220, "protein": 5},
        headers=headers,
    )
    assert response.status_code == 200
    meal_data = client.get("/api/v1/clients/1/meals", headers=headers).json()[0]
    assert meal_data["calories"] == 220
    assert meal_data["protein"] == 5

    response = client.delete(
        f"/api/v1/clients/1/meal/{meal['id']}/items/{item_id}", headers=headers
    )
    assert response.status_code == 204
    meal_data = client.get("/api/v1/clients/1/meals", headers=headers).json()[0]
    assert meal_data["calories"] == 0
    assert meal_data["items"] == []


def test_users_cannot_access_each_others_meal_items(client) -> None:
    owner_headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Itens privados"}, headers=owner_headers)
    meal = client.post(
        "/api/v1/clients/1/meal", json={"meal_date": "2026-01-01"}, headers=owner_headers
    ).json()
    client.post(
        f"/api/v1/clients/1/meal/{meal['id']}/items",
        json={"food_name": "Feijão", "quantity": 100, "unit": "g"},
        headers=owner_headers,
    )
    client.post(
        "/api/v1/auth/register",
        json={"email": "item-other@example.com", "password": "StrongPassword123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": "item-other@example.com", "password": "StrongPassword123"},
    ).json()["access_token"]
    response = client.get(
        f"/api/v1/clients/1/meal/{meal['id']}/items",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_upload_and_get_meal_image(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Imagem"}, headers=headers)
    created = client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01", "calories": 500},
        headers=headers,
    ).json()
    files = {"image": ("almoco.jpg", b"fake-jpeg-content", "image/jpeg")}

    response = client.post(
        f"/api/v1/clients/1/meal/{created['id']}/image",
        files=files,
        headers=headers,
    )
    assert response.status_code == 200
    filename = response.json()["image_url"]
    assert filename.endswith(".jpg")

    response = client.get(
        f"/api/v1/clients/1/meal/{created['id']}/image",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.content == b"fake-jpeg-content"
    assert response.headers["content-type"] == "image/jpeg"


def test_upload_meal_image_rejects_unsupported_type_and_oversized_file(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Validação de imagem"}, headers=headers)
    created = client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01"},
        headers=headers,
    ).json()

    response = client.post(
        f"/api/v1/clients/1/meal/{created['id']}/image",
        files={"image": ("nota.txt", b"text", "text/plain")},
        headers=headers,
    )
    assert response.status_code == 415

    response = client.post(
        f"/api/v1/clients/1/meal/{created['id']}/image",
        files={"image": ("grande.jpg", b"x" * (5 * 1024 * 1024 + 1), "image/jpeg")},
        headers=headers,
    )
    assert response.status_code == 413


def test_users_cannot_access_each_others_meal_images(client) -> None:
    owner_headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Imagem privada"}, headers=owner_headers)
    created = client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01"},
        headers=owner_headers,
    ).json()
    client.post(
        f"/api/v1/clients/1/meal/{created['id']}/image",
        files={"image": ("privada.png", b"private-image", "image/png")},
        headers=owner_headers,
    )

    client.post(
        "/api/v1/auth/register",
        json={"email": "image-other@example.com", "password": "StrongPassword123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": "image-other@example.com", "password": "StrongPassword123"},
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        f"/api/v1/clients/1/meal/{created['id']}/image",
        headers=other_headers,
    )
    assert response.status_code == 404


def test_update_meal_for_client(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Refeição editável"}, headers=headers)
    created = client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01", "calories": 500, "protein": 25},
        headers=headers,
    ).json()

    response = client.put(
        f"/api/v1/clients/1/meal/{created['id']}",
        json={
            "meal_date": "2026-01-02",
            "calories": 700,
            "protein": 40,
            "carbohydrates": 80,
            "fat": 22,
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["meal_date"] == "2026-01-02"
    assert response.json()["calories"] == 700
    assert response.json()["protein"] == 40


def test_delete_meal_for_client(client) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Refeição removível"}, headers=headers)
    created = client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01", "calories": 500},
        headers=headers,
    ).json()

    response = client.delete(f"/api/v1/clients/1/meal/{created['id']}", headers=headers)
    assert response.status_code == 204
    assert client.get("/api/v1/clients/1/meals", headers=headers).json() == []

    response = client.delete(f"/api/v1/clients/1/meal/{created['id']}", headers=headers)
    assert response.status_code == 404


def test_users_cannot_update_or_delete_each_others_meals(client) -> None:
    owner_headers = auth_headers(client)
    client.post("/api/v1/clients", json={"name": "Refeição privada"}, headers=owner_headers)
    client.post(
        "/api/v1/clients/1/meal",
        json={"meal_date": "2026-01-01", "calories": 500},
        headers=owner_headers,
    )

    client.post(
        "/api/v1/auth/register",
        json={"email": "meal-other@example.com", "password": "StrongPassword123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": "meal-other@example.com", "password": "StrongPassword123"},
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {token}"}

    response = client.put(
        "/api/v1/clients/1/meal/1",
        json={"meal_date": "2026-01-02", "calories": 700},
        headers=other_headers,
    )
    assert response.status_code == 404

    response = client.delete("/api/v1/clients/1/meal/1", headers=other_headers)
    assert response.status_code == 404
    assert len(client.get("/api/v1/clients/1/meals", headers=owner_headers).json()) == 1


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
