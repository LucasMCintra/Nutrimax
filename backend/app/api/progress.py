from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db import get_db
from app.models import Client, Meal, NutritionTarget, User
from app.schemas import ProgressPoint, ProgressResponse

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("", response_model=ProgressResponse)
def get_progress(
    start_date: date,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    end = end_date or start_date + timedelta(days=6)
    if end < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be on or after start_date",
        )
    if (end - start_date).days > 30:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The maximum progress range is 31 days",
        )

    client = db.execute(select(Client).where(Client.user_id == current_user.id)).scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found")

    target = db.execute(
        select(NutritionTarget).where(NutritionTarget.client_id == client.id)
    ).scalar_one_or_none()
    rows = db.execute(
        select(
            Meal.meal_date,
            func.coalesce(func.sum(Meal.calories), 0),
            func.coalesce(func.sum(Meal.protein), 0),
            func.coalesce(func.sum(Meal.carbohydrates), 0),
            func.coalesce(func.sum(Meal.fat), 0),
        )
        .where(Meal.client_id == client.id, Meal.meal_date.between(start_date, end))
        .group_by(Meal.meal_date)
    ).all()
    totals = {row[0]: row[1:] for row in rows}
    points = []
    current = start_date
    while current <= end:
        values = totals.get(current, (0, 0, 0, 0))
        points.append(
            ProgressPoint(
                date=current,
                calories=float(values[0]),
                protein=float(values[1]),
                carbohydrates=float(values[2]),
                fat=float(values[3]),
            )
        )
        current += timedelta(days=1)

    return ProgressResponse(
        start_date=start_date,
        end_date=end,
        target=target,
        points=points,
    )
