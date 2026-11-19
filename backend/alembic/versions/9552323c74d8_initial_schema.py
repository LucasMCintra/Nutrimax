"""initial schema

Revision ID: 9552323c74d8
Revises:
Create Date: 2026-11-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9552323c74d8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("weight", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("height", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
    )
    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.UniqueConstraint("client_id"),
    )
    op.create_table(
        "diets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.UniqueConstraint("client_id"),
    )
    op.create_table(
        "meals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("meal_date", sa.Date(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
    )


def downgrade() -> None:
    op.drop_table("meals")
    op.drop_table("diets")
    op.drop_table("goals")
    op.drop_table("clients")
