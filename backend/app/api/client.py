from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.api.auth import get_current_user
from app.db import get_db
from app.models import User
from app.schemas import (
    ClientCreate,
    ClientRead,
    ClientUpdate,
    ClientWithRelations,
    DietCreate,
    DietRead,
    GoalCreate,
    GoalRead,
    MealCreate,
    MealRead,
)

router = APIRouter(prefix="/clients", tags=["Clients"])


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