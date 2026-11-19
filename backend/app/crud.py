from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Client, Diet, Goal, Meal
from app.schemas import (
    ClientCreate,
    ClientUpdate,
    DietCreate,
    GoalCreate,
    MealCreate,
)


def get_client(db: Session, client_id: int) -> Client | None:
    return db.get(Client, client_id)


def get_client_by_id(db: Session, client_id: int) -> Client | None:
    return get_client(db, client_id)


def get_clients(db: Session, skip: int = 0, limit: int = 100) -> list[Client]:
    return db.execute(select(Client).offset(skip).limit(limit)).scalars().all()


def create_client(db: Session, client: ClientCreate) -> Client:
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(db: Session, client_id: int, client: ClientUpdate) -> Client | None:
    db_client = get_client(db, client_id)
    if db_client is None:
        return None
    update_data = client.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int) -> bool:
    db_client = get_client(db, client_id)
    if db_client is None:
        return False
    db.delete(db_client)
    db.commit()
    return True


def create_goal(db: Session, goal: GoalCreate) -> Goal:
    db_goal = Goal(**goal.model_dump())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def get_goal_by_client(db: Session, client_id: int) -> Goal | None:
    return db.execute(
        select(Goal).where(Goal.client_id == client_id)
    ).scalar_one_or_none()


def create_diet(db: Session, diet: DietCreate) -> Diet:
    db_diet = Diet(**diet.model_dump())
    db.add(db_diet)
    db.commit()
    db.refresh(db_diet)
    return db_diet


def get_diet_by_client(db: Session, client_id: int) -> Diet | None:
    return db.execute(
        select(Diet).where(Diet.client_id == client_id)
    ).scalar_one_or_none()


def create_meal(db: Session, meal: MealCreate) -> Meal:
    db_meal = Meal(**meal.model_dump())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def get_meal(db: Session, meal_id: int) -> Meal | None:
    return db.get(Meal, meal_id)


def get_meals_by_client(db: Session, client_id: int) -> list[Meal]:
    return (
        db.execute(select(Meal).where(Meal.client_id == client_id))
        .scalars()
        .all()
    )