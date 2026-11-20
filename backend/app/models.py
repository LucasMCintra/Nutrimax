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
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    client: Mapped[Optional["Client"]] = relationship(
        back_populates="user", uselist=False
    )


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    weight: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    height: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    age: Mapped[Optional[int]]

    user: Mapped[Optional[User]] = relationship(back_populates="client")
    goal: Mapped[Optional["Goal"]] = relationship(
        back_populates="client", uselist=False, cascade="all, delete-orphan"
    )
    diet: Mapped[Optional["Diet"]] = relationship(
        back_populates="client", uselist=False, cascade="all, delete-orphan"
    )
    meals: Mapped[list["Meal"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )


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


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    meal_date: Mapped[date] = mapped_column(Date, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    client: Mapped[Client] = relationship(back_populates="meals")
