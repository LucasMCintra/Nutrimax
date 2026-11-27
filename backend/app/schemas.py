from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ClientBase(BaseModel):
    name: str = Field(..., max_length=120)
    weight: Optional[float] = Field(default=None, gt=0)
    height: Optional[float] = Field(default=None, gt=0)
    age: Optional[int] = Field(default=None, gt=0)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=120)
    weight: Optional[float] = Field(default=None, gt=0)
    height: Optional[float] = Field(default=None, gt=0)
    age: Optional[int] = Field(default=None, gt=0)


class ClientRead(ClientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class GoalBase(BaseModel):
    description: str = Field(..., max_length=120)


class GoalCreate(GoalBase):
    client_id: Optional[int] = None


class GoalUpdate(GoalBase):
    pass


class GoalRead(GoalBase):
    id: int
    client_id: int
    model_config = ConfigDict(from_attributes=True)


class DietBase(BaseModel):
    description: str


class DietCreate(DietBase):
    client_id: Optional[int] = None


class DietUpdate(DietBase):
    pass


class DietRead(DietBase):
    id: int
    client_id: int
    model_config = ConfigDict(from_attributes=True)


class NutritionTargetBase(BaseModel):
    calories: float = Field(..., gt=0)
    protein: float = Field(..., ge=0)
    carbohydrates: float = Field(..., ge=0)
    fat: float = Field(..., ge=0)


class NutritionTargetCreate(NutritionTargetBase):
    pass


class NutritionTargetRead(NutritionTargetBase):
    id: int
    client_id: int
    model_config = ConfigDict(from_attributes=True)


class MealBase(BaseModel):
    meal_date: date
    image_url: Optional[str] = Field(default=None, max_length=500)
    calories: float = Field(default=0, ge=0)
    protein: float = Field(default=0, ge=0)
    carbohydrates: float = Field(default=0, ge=0)
    fat: float = Field(default=0, ge=0)


class MealCreate(MealBase):
    client_id: Optional[int] = None


class MealUpdate(MealBase):
    pass


class MealItemBase(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=120)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=30)
    calories: float = Field(default=0, ge=0)
    protein: float = Field(default=0, ge=0)
    carbohydrates: float = Field(default=0, ge=0)
    fat: float = Field(default=0, ge=0)


class MealItemCreate(MealItemBase):
    pass


class MealItemRead(MealItemBase):
    id: int
    meal_id: int
    model_config = ConfigDict(from_attributes=True)


class MealAnalysisItemBase(MealItemBase):
    confidence: Optional[float] = Field(default=None, ge=0, le=1)


class MealAnalysisItemRead(MealAnalysisItemBase):
    id: int
    analysis_id: int
    model_config = ConfigDict(from_attributes=True)


class MealAnalysisRead(BaseModel):
    id: int
    meal_id: int
    status: Literal["pending", "completed", "failed", "confirmed"]
    provider: str
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    items: list[MealAnalysisItemRead] = []
    model_config = ConfigDict(from_attributes=True)


class MealRead(MealBase):
    id: int
    client_id: int
    items: list[MealItemRead] = []
    analyses: list[MealAnalysisRead] = []
    model_config = ConfigDict(from_attributes=True)


class MealAnalysisConfirm(BaseModel):
    item_ids: list[int] = Field(default_factory=list)


class ClientWithRelations(ClientRead):
    goal: Optional[GoalRead] = None
    diet: Optional[DietRead] = None
    nutrition_target: Optional[NutritionTargetRead] = None
    meals: list[MealRead] = []


class ProgressPoint(BaseModel):
    date: date
    calories: float
    protein: float
    carbohydrates: float
    fat: float


class ProgressResponse(BaseModel):
    start_date: date
    end_date: date
    target: Optional[NutritionTargetRead] = None
    points: list[ProgressPoint]
