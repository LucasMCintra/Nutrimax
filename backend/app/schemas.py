from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ClientBase(BaseModel):
    name: str = Field(..., max_length=120)
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=120)
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None


class ClientRead(ClientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class GoalBase(BaseModel):
    description: str = Field(..., max_length=120)


class GoalCreate(GoalBase):
    client_id: int


class GoalRead(GoalBase):
    id: int
    client_id: int

    model_config = ConfigDict(from_attributes=True)


class DietBase(BaseModel):
    description: str


class DietCreate(DietBase):
    client_id: int


class DietRead(DietBase):
    id: int
    client_id: int

    model_config = ConfigDict(from_attributes=True)


class MealBase(BaseModel):
    client_id: int
    meal_date: date
    image_url: Optional[str] = None


class MealCreate(MealBase):
    pass


class MealRead(MealBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ClientWithRelations(ClientRead):
    goal: Optional[GoalRead] = None
    diet: Optional[DietRead] = None
    meals: list[MealRead] = []