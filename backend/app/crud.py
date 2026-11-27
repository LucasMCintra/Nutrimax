from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Client, Diet, Goal, Meal, MealAnalysis, MealAnalysisItem, MealItem, User
from app.schemas import ClientCreate, ClientUpdate, DietCreate, DietUpdate, GoalCreate, MealAnalysisItemBase, MealCreate, MealItemCreate, MealUpdate


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


def get_diet(db: Session, client_id: int, user_id: int) -> Diet | None:
    return db.execute(
        select(Diet)
        .join(Client)
        .where(Diet.client_id == client_id, Client.user_id == user_id)
    ).scalar_one_or_none()


def update_diet(db: Session, client_id: int, diet: DietUpdate, user_id: int) -> Diet | None:
    db_diet = get_diet(db, client_id, user_id)
    if db_diet is None:
        return None
    db_diet.description = diet.description
    db.commit()
    db.refresh(db_diet)
    return db_diet


def delete_diet(db: Session, client_id: int, user_id: int) -> bool:
    db_diet = get_diet(db, client_id, user_id)
    if db_diet is None:
        return False
    db.delete(db_diet)
    db.commit()
    return True


def create_meal(db: Session, meal: MealCreate, user_id: int) -> Meal | None:
    if get_client(db, meal.client_id, user_id) is None:
        return None
    db_meal = Meal(**meal.model_dump())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def get_meal(db: Session, client_id: int, meal_id: int, user_id: int) -> Meal | None:
    return db.execute(
        select(Meal)
        .join(Client)
        .where(
            Meal.id == meal_id,
            Meal.client_id == client_id,
            Client.user_id == user_id,
        )
    ).scalar_one_or_none()


def update_meal(
    db: Session, client_id: int, meal_id: int, meal: MealUpdate, user_id: int
) -> Meal | None:
    db_meal = get_meal(db, client_id, meal_id, user_id)
    if db_meal is None:
        return None
    for field, value in meal.model_dump(exclude={"client_id"}).items():
        setattr(db_meal, field, value)
    db.commit()
    db.refresh(db_meal)
    return db_meal


def delete_meal(db: Session, client_id: int, meal_id: int, user_id: int) -> bool:
    db_meal = get_meal(db, client_id, meal_id, user_id)
    if db_meal is None:
        return False
    db.delete(db_meal)
    db.commit()
    return True


def recalculate_meal_totals(db: Session, meal: Meal) -> Meal:
    meal.calories = sum(item.calories for item in meal.items)
    meal.protein = sum(item.protein for item in meal.items)
    meal.carbohydrates = sum(item.carbohydrates for item in meal.items)
    meal.fat = sum(item.fat for item in meal.items)
    return meal


def get_meal_item(db: Session, client_id: int, meal_id: int, item_id: int, user_id: int) -> MealItem | None:
    return db.execute(
        select(MealItem)
        .join(Meal)
        .join(Client)
        .where(
            MealItem.id == item_id,
            MealItem.meal_id == meal_id,
            Meal.client_id == client_id,
            Client.user_id == user_id,
        )
    ).scalar_one_or_none()


def create_meal_item(db: Session, client_id: int, meal_id: int, item: MealItemCreate, user_id: int) -> MealItem | None:
    db_meal = get_meal(db, client_id, meal_id, user_id)
    if db_meal is None:
        return None
    db_item = MealItem(meal_id=meal_id, **item.model_dump())
    db.add(db_item)
    db.flush()
    recalculate_meal_totals(db, db_meal)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_meal_item(db: Session, client_id: int, meal_id: int, item_id: int, item: MealItemCreate, user_id: int) -> MealItem | None:
    db_item = get_meal_item(db, client_id, meal_id, item_id, user_id)
    if db_item is None:
        return None
    for field, value in item.model_dump().items():
        setattr(db_item, field, value)
    recalculate_meal_totals(db, db_item.meal)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_meal_item(db: Session, client_id: int, meal_id: int, item_id: int, user_id: int) -> bool:
    db_item = get_meal_item(db, client_id, meal_id, item_id, user_id)
    if db_item is None:
        return False
    db_meal = db_item.meal
    db.delete(db_item)
    db.flush()
    recalculate_meal_totals(db, db_meal)
    db.commit()
    return True


def get_meal_analysis(db: Session, client_id: int, meal_id: int, analysis_id: int, user_id: int) -> MealAnalysis | None:
    return db.execute(
        select(MealAnalysis)
        .join(Meal)
        .join(Client)
        .where(
            MealAnalysis.id == analysis_id,
            MealAnalysis.meal_id == meal_id,
            Meal.client_id == client_id,
            Client.user_id == user_id,
        )
    ).scalar_one_or_none()


def create_pending_analysis(db: Session, client_id: int, meal_id: int, user_id: int) -> MealAnalysis | None:
    if get_meal(db, client_id, meal_id, user_id) is None:
        return None
    existing = db.execute(
        select(MealAnalysis)
        .join(Meal)
        .join(Client)
        .where(
            MealAnalysis.meal_id == meal_id,
            MealAnalysis.status == "pending",
            Meal.client_id == client_id,
            Client.user_id == user_id,
        )
        .order_by(MealAnalysis.created_at.desc())
    ).scalars().first()
    if existing is not None:
        return existing
    analysis = MealAnalysis(meal_id=meal_id, status="pending", provider="manual")
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def fail_analysis(db: Session, analysis: MealAnalysis, message: str) -> MealAnalysis:
    analysis.status = "failed"
    analysis.error_message = message[:500]
    db.commit()
    db.refresh(analysis)
    return analysis


def complete_analysis(
    db: Session,
    client_id: int,
    meal_id: int,
    analysis_id: int,
    items: list[MealAnalysisItemBase],
    user_id: int,
    provider: str = "manual",
) -> MealAnalysis | None:
    analysis = get_meal_analysis(db, client_id, meal_id, analysis_id, user_id)
    if analysis is None:
        return None
    analysis.items.clear()
    analysis.items.extend(MealAnalysisItem(**item.model_dump()) for item in items)
    analysis.status = "completed"
    analysis.provider = provider
    analysis.error_message = None
    from datetime import datetime, timezone
    analysis.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(analysis)
    return analysis


def confirm_analysis(db: Session, client_id: int, meal_id: int, analysis_id: int, item_ids: list[int], user_id: int) -> Meal | None:
    analysis = get_meal_analysis(db, client_id, meal_id, analysis_id, user_id)
    if analysis is None or analysis.status != "completed":
        return None
    selected = [item for item in analysis.items if not item_ids or item.id in item_ids]
    meal = analysis.meal
    meal.items.clear()
    meal.items.extend(
        MealItem(
            food_name=item.food_name,
            quantity=item.quantity,
            unit=item.unit,
            calories=item.calories,
            protein=item.protein,
            carbohydrates=item.carbohydrates,
            fat=item.fat,
        )
        for item in selected
    )
    recalculate_meal_totals(db, meal)
    analysis.status = "confirmed"
    db.commit()
    db.refresh(meal)
    return meal


def get_meal_items(db: Session, client_id: int, meal_id: int, user_id: int) -> list[MealItem] | None:
    db_meal = get_meal(db, client_id, meal_id, user_id)
    if db_meal is None:
        return None
    return db_meal.items


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