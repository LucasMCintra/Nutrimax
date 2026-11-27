from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    client: Mapped[Optional["Client"]] = relationship(back_populates="user", uselist=False)


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    weight: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    height: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    age: Mapped[Optional[int]]

    user: Mapped[Optional[User]] = relationship(back_populates="client")
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="client", uselist=False, cascade="all, delete-orphan")
    diet: Mapped[Optional["Diet"]] = relationship(back_populates="client", uselist=False, cascade="all, delete-orphan")
    nutrition_target: Mapped[Optional["NutritionTarget"]] = relationship(back_populates="client", uselist=False, cascade="all, delete-orphan")
    meals: Mapped[list["Meal"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), unique=True)
    description: Mapped[str] = mapped_column(String(120), nullable=False)

    client: Mapped[Client] = relationship(back_populates="goal")


class Diet(Base):
    __tablename__ = "diets"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    client: Mapped[Client] = relationship(back_populates="diet")


class NutritionTarget(Base):
    __tablename__ = "nutrition_targets"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), unique=True)
    calories: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    protein: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    carbohydrates: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    fat: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)

    client: Mapped[Client] = relationship(back_populates="nutrition_target")


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    meal_date: Mapped[date] = mapped_column(Date, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    calories: Mapped[float] = mapped_column(Numeric(8, 2), default=0, server_default="0", nullable=False)
    protein: Mapped[float] = mapped_column(Numeric(8, 2), default=0, server_default="0", nullable=False)
    carbohydrates: Mapped[float] = mapped_column(Numeric(8, 2), default=0, server_default="0", nullable=False)
    fat: Mapped[float] = mapped_column(Numeric(8, 2), default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    client: Mapped[Client] = relationship(back_populates="meals")
    items: Mapped[list["MealItem"]] = relationship(back_populates="meal", cascade="all, delete-orphan")
    analyses: Mapped[list["MealAnalysis"]] = relationship(back_populates="meal", cascade="all, delete-orphan")


class MealItem(Base):
    __tablename__ = "meal_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.id"), nullable=False)
    food_name: Mapped[str] = mapped_column(String(120), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    calories: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    protein: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    carbohydrates: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    fat: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)

    meal: Mapped[Meal] = relationship(back_populates="items")


class MealAnalysis(Base):
    __tablename__ = "meal_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    provider: Mapped[str] = mapped_column(String(40), nullable=False, default="manual")
    error_message: Mapped[Optional[str]] = mapped_column(String(500))
    error_code: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    meal: Mapped[Meal] = relationship(back_populates="analyses")
    items: Mapped[list["MealAnalysisItem"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")


class MealAnalysisItem(Base):
    __tablename__ = "meal_analysis_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("meal_analyses.id"), nullable=False)
    food_name: Mapped[str] = mapped_column(String(120), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    calories: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    protein: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    carbohydrates: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    fat: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))

    analysis: Mapped[MealAnalysis] = relationship(back_populates="items")
