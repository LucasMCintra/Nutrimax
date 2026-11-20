from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db import get_db
from app.models import Client, Meal, NutritionTarget, User
from app.schemas import NutritionTargetCreate, NutritionTargetRead

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_owned_client(db: Session, user: User) -> Client:
    client = db.execute(select(Client).where(Client.user_id == user.id)).scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found")
    return client


@router.put("/target", response_model=NutritionTargetRead)
def set_nutrition_target(
    payload: NutritionTargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NutritionTarget:
    client = get_owned_client(db, current_user)
    target = db.execute(
        select(NutritionTarget).where(NutritionTarget.client_id == client.id)
    ).scalar_one_or_none()
    if target is None:
        target = NutritionTarget(client_id=client.id, **payload.model_dump())
        db.add(target)
    else:
        for field, value in payload.model_dump().items():
            setattr(target, field, value)
    db.commit()
    db.refresh(target)
    return target


@router.get("/summary")
def get_dashboard_summary(
    reference_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    client = get_owned_client(db, current_user)
    day = reference_date or date.today()
    week_start = day - timedelta(days=day.weekday())
    month_start = day.replace(day=1)
    target = db.execute(
        select(NutritionTarget).where(NutritionTarget.client_id == client.id)
    ).scalar_one_or_none()

    def totals(start: date, end: date) -> dict[str, float]:
        values = db.execute(
            select(
                func.coalesce(func.sum(Meal.calories), 0),
                func.coalesce(func.sum(Meal.protein), 0),
                func.coalesce(func.sum(Meal.carbohydrates), 0),
                func.coalesce(func.sum(Meal.fat), 0),
            ).where(
                Meal.client_id == client.id,
                Meal.meal_date >= start,
                Meal.meal_date <= end,
            )
        ).one()
        return {
            "calories": float(values[0]),
            "protein": float(values[1]),
            "carbohydrates": float(values[2]),
            "fat": float(values[3]),
        }

    return {
        "date": day,
        "target": NutritionTargetRead.model_validate(target) if target else None,
        "day": totals(day, day),
        "week": totals(week_start, week_start + timedelta(days=6)),
        "month": totals(month_start, (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)),
    }
