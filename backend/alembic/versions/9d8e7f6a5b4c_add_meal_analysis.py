"""add meal analysis

Revision ID: 9d8e7f6a5b4c
Revises: 8c7f1a2b3d4e

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d8e7f6a5b4c"
down_revision: Union[str, None] = "8c7f1a2b3d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "meal_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("meal_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["meal_id"], ["meals.id"]),
    )
    op.create_table(
        "meal_analysis_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("analysis_id", sa.Integer(), nullable=False),
        sa.Column("food_name", sa.String(length=120), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=False),
        sa.Column("calories", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("protein", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("carbohydrates", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("fat", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.ForeignKeyConstraint(["analysis_id"], ["meal_analyses.id"]),
    )


def downgrade() -> None:
    op.drop_table("meal_analysis_items")
    op.drop_table("meal_analyses")
