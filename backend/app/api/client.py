from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.api.auth import get_current_user
from app.db import get_db
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

router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)) -> ClientRead:
    return crud.create_client(db, payload)


@router.get("", response_model=list[ClientRead])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[ClientRead]:
    return crud.get_clients(db, skip=skip, limit=limit)


@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(get_db)) -> ClientRead:
    db_client = crud.get_client_by_id(db, client_id)
    if db_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return db_client


@router.get("/{client_id}/full", response_model=ClientWithRelations)
def get_client_full(client_id: int, db: Session = Depends(get_db)) -> ClientWithRelations:
    db_client = crud.get_client_by_id(db, client_id)
    if db_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return db_client


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
) -> ClientRead:
    db_client = crud.update_client(db, client_id, payload)
    if db_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return db_client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_client(client_id: int, db: Session = Depends(get_db)) -> Response:
    deleted = crud.delete_client(db, client_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{client_id}/goal", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(client_id: int, payload: GoalCreate, db: Session = Depends(get_db)):
    if crud.get_client_by_id(db, client_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    payload_data = payload.model_dump()
    payload_data["client_id"] = client_id
    return crud.create_goal(db, GoalCreate(**payload_data))


@router.post("/{client_id}/diet", response_model=DietRead, status_code=status.HTTP_201_CREATED)
def create_diet(client_id: int, payload: DietCreate, db: Session = Depends(get_db)):
    if crud.get_client_by_id(db, client_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    payload_data = payload.model_dump()
    payload_data["client_id"] = client_id
    return crud.create_diet(db, DietCreate(**payload_data))


@router.post("/{client_id}/meal", response_model=MealRead, status_code=status.HTTP_201_CREATED)
def create_meal(client_id: int, payload: MealCreate, db: Session = Depends(get_db)):
    if crud.get_client_by_id(db, client_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    payload_data = payload.model_dump()
    payload_data["client_id"] = client_id
    return crud.create_meal(db, MealCreate(**payload_data))