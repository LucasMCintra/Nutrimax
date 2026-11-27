"""add analysis error code

Revision ID: b2c3d4e5f6a7
Revises: 9d8e7f6a5b4c

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "9d8e7f6a5b4c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("meal_analyses", sa.Column("error_code", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("meal_analyses", "error_code")
