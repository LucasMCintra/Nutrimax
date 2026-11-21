from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Client, Diet, Goal, Meal, User
from app.schemas import ClientCreate, ClientUpdate, DietCreate, GoalCreate, MealCreate


def get_client(db: Session, client_id: int, user_id: int | None = None) -> Client | None:
    query = select(Client).where(Client.id == client_id)
    if user_id is not None:
        query = query.where(Client.user_id == user_id)
    return db.execute(query).scalar_one_or_none()


def get_client_by_id(db: Session, client_id: int, user_id: int | None = None) -> Client | None:
    return get_client(db, client_id, user_id)


def get_clients(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Client]:
    return (
        db.execute(
            select(Client).where(Client.user_id == user_id).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )


def create_client(db: Session, client: ClientCreate, user: User) -> Client | None:
    if db.execute(select(Client).where(Client.user_id == user.id)).scalar_one_or_none():
        return None
    db_client = Client(**client.model_dump(), user_id=user.id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(
    db: Session, client_id: int, client: ClientUpdate, user_id: int
) -> Client | None:
    db_client = get_client(db, client_id, user_id)
    if db_client is None:
        return None
    for field, value in client.model_dump(exclude_unset=True).items():
        setattr(db_client, field, value)
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int, user_id: int) -> bool:
    db_client = get_client(db, client_id, user_id)
    if db_client is None:
        return False
    db.delete(db_client)
    db.commit()
    return True


def create_goal(db: Session, goal: GoalCreate, user_id: int) -> Goal | None:
    if get_client(db, goal.client_id, user_id) is None:
        return None
    db_goal = Goal(**goal.model_dump())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def update_goal(db: Session, client_id: int, description: str, user_id: int) -> Goal | None:
    db_client = get_client(db, client_id, user_id)
    if db_client is None:
        return None
    db_goal = db_client.goal
    if db_goal is None:
        db_goal = Goal(client_id=client_id, description=description)
        db.add(db_goal)
    else:
        db_goal.description = description
    db.commit()
    db.refresh(db_goal)
    return db_goal


def create_diet(db: Session, diet: DietCreate, user_id: int) -> Diet | None:
    if get_client(db, diet.client_id, user_id) is None:
        return None
    db_diet = Diet(**diet.model_dump())
    db.add(db_diet)
    db.commit()
    db.refresh(db_diet)
    return db_diet


def create_meal(db: Session, meal: MealCreate, user_id: int) -> Meal | None:
    if get_client(db, meal.client_id, user_id) is None:
        return None
    db_meal = Meal(**meal.model_dump())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def get_meals_by_client(db: Session, client_id: int, user_id: int) -> list[Meal]:
    return (
        db.execute(
            select(Meal)
            .join(Client)
            .where(Meal.client_id == client_id, Client.user_id == user_id)
        )
        .scalars()
        .all()
    )