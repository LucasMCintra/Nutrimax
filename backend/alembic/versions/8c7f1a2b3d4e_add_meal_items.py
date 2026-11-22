"""add meal items

Revision ID: 8c7f1a2b3d4e
Revises: 7b2c4d8e1f90

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c7f1a2b3d4e"
down_revision: Union[str, None] = "7b2c4d8e1f90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "meal_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("meal_id", sa.Integer(), nullable=False),
        sa.Column("food_name", sa.String(length=120), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=False),
        sa.Column("calories", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("protein", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("carbohydrates", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("fat", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["meal_id"], ["meals.id"]),
    )


def downgrade() -> None:
    op.drop_table("meal_items")
