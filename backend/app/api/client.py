from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import crud
from app.ai_provider import AnalysisProviderError, GoogleAIStudioProvider, MealImage
from app.api.auth import get_current_user
from app.db import get_db
from app.core.config import settings
from app.models import User
from app.storage import resolve_image, save_image
from app.schemas import (
    ClientCreate,
    ClientRead,
    ClientUpdate,
    ClientWithRelations,
    DietCreate,
    DietRead,
    DietUpdate,
    GoalCreate,
    GoalRead,
    GoalUpdate,
    MealAnalysisConfirm,
    MealAnalysisItemBase,
    MealAnalysisRead,
    MealCreate,
    MealItemCreate,
    MealItemRead,
    MealRead,
    MealUpdate,
)

router = APIRouter(prefix="/clients", tags=["Clients"])


def get_upload_dir() -> Path:
    return Path(settings.upload_dir)


def get_meal_image_bytes(meal, user_id: int) -> tuple[bytes, str] | None:
    if not meal.image_url:
        return None
    image_path = resolve_image(get_upload_dir() / str(user_id), meal.image_url)
    if image_path is None:
        return None
    mime_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(image_path.suffix.lower())
    if mime_type is None:
        return None
    return image_path.read_bytes(), mime_type


def require_client(client_id: int, user: User, db: Session):
    db_client = crud.get_client_by_id(db, client_id, user.id)
    if db_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return db_client


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientRead:
    client = crud.create_client(db, payload, current_user)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A client profile already exists for this user",
        )
    return client


@router.get("", response_model=list[ClientRead])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClientRead]:
    return crud.get_clients(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientRead:
    return require_client(client_id, current_user, db)


@router.get("/{client_id}/full", response_model=ClientWithRelations)
def get_client_full(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientWithRelations:
    return require_client(client_id, current_user, db)


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientRead:
    db_client = crud.update_client(db, client_id, payload, current_user.id)
    if db_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return db_client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    if not crud.delete_client(db, client_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{client_id}/goal", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    client_id: int,
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload_data = payload.model_dump()
    payload_data["client_id"] = client_id
    goal = crud.create_goal(db, GoalCreate(**payload_data), current_user.id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return goal


@router.put("/{client_id}/goal", response_model=GoalRead)
def update_goal(
    client_id: int,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = crud.update_goal(db, client_id, payload.description, current_user.id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return goal


@router.post("/{client_id}/diet", response_model=DietRead, status_code=status.HTTP_201_CREATED)
def create_diet(
    client_id: int,
    payload: DietCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload_data = payload.model_dump()
    payload_data["client_id"] = client_id
    diet = crud.create_diet(db, DietCreate(**payload_data), current_user.id)
    if diet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return diet


@router.get("/{client_id}/diet", response_model=DietRead)
def get_diet(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diet = crud.get_diet(db, client_id, current_user.id)
    if diet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet not found")
    return diet


@router.put("/{client_id}/diet", response_model=DietRead)
def update_diet(
    client_id: int,
    payload: DietUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diet = crud.update_diet(db, client_id, payload, current_user.id)
    if diet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet not found")
    return diet


@router.delete("/{client_id}/diet", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_diet(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    if not crud.delete_diet(db, client_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{client_id}/meals", response_model=list[MealRead])
def list_meals(
    client_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MealRead]:
    require_client(client_id, current_user, db)
    meals = crud.get_meals_by_client(db, client_id, current_user.id)
    return meals[skip : skip + limit]


@router.post("/{client_id}/meal", response_model=MealRead, status_code=status.HTTP_201_CREATED)
def create_meal(
    client_id: int,
    payload: MealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload_data = payload.model_dump()
    payload_data["client_id"] = client_id
    meal = crud.create_meal(db, MealCreate(**payload_data), current_user.id)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return meal


@router.post("/{client_id}/meal/{meal_id}/image", response_model=MealRead)
def upload_meal_image(
    client_id: int,
    meal_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meal = crud.get_meal(db, client_id, meal_id, current_user.id)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    filename, _ = save_image(image, get_upload_dir() / str(current_user.id))
    meal.image_url = filename
    db.commit()
    db.refresh(meal)
    return meal


@router.get("/{client_id}/meal/{meal_id}/image")
def get_meal_image(
    client_id: int,
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meal = crud.get_meal(db, client_id, meal_id, current_user.id)
    if meal is None or not meal.image_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal image not found")
    image_path = resolve_image(get_upload_dir() / str(current_user.id), meal.image_url)
    if image_path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal image not found")
    return FileResponse(image_path)


@router.put("/{client_id}/meal/{meal_id}", response_model=MealRead)
def update_meal(
    client_id: int,
    meal_id: int,
    payload: MealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meal = crud.update_meal(db, client_id, meal_id, payload, current_user.id)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return meal


@router.get("/{client_id}/meal/{meal_id}/analysis", response_model=list[MealAnalysisRead])
def list_meal_analyses(
    client_id: int,
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analyses = crud.get_meal_analyses(db, client_id, meal_id, current_user.id)
    if analyses is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return analyses


@router.post("/{client_id}/meal/{meal_id}/analysis", response_model=MealAnalysisRead, status_code=status.HTTP_201_CREATED)
def create_meal_analysis(
    client_id: int,
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = crud.create_pending_analysis(db, client_id, meal_id, current_user.id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return analysis


@router.post("/{client_id}/meal/{meal_id}/analysis/{analysis_id}/run", response_model=MealAnalysisRead)
def run_meal_analysis(
    client_id: int,
    meal_id: int,
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = crud.get_meal_analysis(db, client_id, meal_id, analysis_id, current_user.id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    if analysis.status == "confirmed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Analysis is already confirmed")
    meal = crud.get_meal(db, client_id, meal_id, current_user.id)
    image = get_meal_image_bytes(meal, current_user.id) if meal else None
    if image is None:
        crud.fail_analysis(db, analysis, "Meal image not found", error_code="image_required")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Meal image is required for analysis")
    try:
        items = GoogleAIStudioProvider().analyze_meal(MealImage(data=image[0], mime_type=image[1]))
        return crud.complete_analysis(
            db, client_id, meal_id, analysis_id, items, current_user.id, provider="google_ai_studio"
        )
    except AnalysisProviderError as error:
        failed = crud.fail_analysis(db, analysis, str(error), error_code=error.code)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=failed.error_message, headers={"X-Analysis-Error-Code": error.code}) from error


@router.put("/{client_id}/meal/{meal_id}/analysis/{analysis_id}", response_model=MealAnalysisRead)
def complete_meal_analysis(
    client_id: int,
    meal_id: int,
    analysis_id: int,
    payload: list[MealAnalysisItemBase],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = crud.complete_analysis(db, client_id, meal_id, analysis_id, payload, current_user.id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return analysis


@router.post("/{client_id}/meal/{meal_id}/analysis/{analysis_id}/confirm", response_model=MealRead)
def confirm_meal_analysis(
    client_id: int,
    meal_id: int,
    analysis_id: int,
    payload: MealAnalysisConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = crud.get_meal_analysis(db, client_id, meal_id, analysis_id, current_user.id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    if analysis.status == "confirmed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Analysis is already confirmed")
    meal = crud.confirm_analysis(db, client_id, meal_id, analysis_id, payload.item_ids, current_user.id)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only a completed analysis can be confirmed")
    return meal


@router.get("/{client_id}/meal/{meal_id}/items", response_model=list[MealItemRead])
def list_meal_items(
    client_id: int,
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = crud.get_meal_items(db, client_id, meal_id, current_user.id)
    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return items


@router.post("/{client_id}/meal/{meal_id}/items", response_model=MealItemRead, status_code=status.HTTP_201_CREATED)
def create_meal_item(
    client_id: int,
    meal_id: int,
    payload: MealItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = crud.create_meal_item(db, client_id, meal_id, payload, current_user.id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return item


@router.put("/{client_id}/meal/{meal_id}/items/{item_id}", response_model=MealItemRead)
def update_meal_item(
    client_id: int,
    meal_id: int,
    item_id: int,
    payload: MealItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = crud.update_meal_item(db, client_id, meal_id, item_id, payload, current_user.id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal item not found")
    return item


@router.delete("/{client_id}/meal/{meal_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_meal_item(
    client_id: int,
    meal_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    if not crud.delete_meal_item(db, client_id, meal_id, item_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal item not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{client_id}/meal/{meal_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_meal(
    client_id: int,
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    if not crud.delete_meal(db, client_id, meal_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
