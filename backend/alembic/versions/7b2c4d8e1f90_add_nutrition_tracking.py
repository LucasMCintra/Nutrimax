"""add nutrition tracking

Revision ID: 7b2c4d8e1f90
Revises: 4f1e8a2c9d10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b2c4d8e1f90"
down_revision: Union[str, None] = "4f1e8a2c9d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "nutrition_targets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("calories", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("protein", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("carbohydrates", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("fat", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.UniqueConstraint("client_id"),
    )
    op.add_column("meals", sa.Column("calories", sa.Numeric(precision=8, scale=2), server_default="0", nullable=False))
    op.add_column("meals", sa.Column("protein", sa.Numeric(precision=8, scale=2), server_default="0", nullable=False))
    op.add_column("meals", sa.Column("carbohydrates", sa.Numeric(precision=8, scale=2), server_default="0", nullable=False))
    op.add_column("meals", sa.Column("fat", sa.Numeric(precision=8, scale=2), server_default="0", nullable=False))


def downgrade() -> None:
    op.drop_column("meals", "fat")
    op.drop_column("meals", "carbohydrates")
    op.drop_column("meals", "protein")
    op.drop_column("meals", "calories")
    op.drop_table("nutrition_targets")
