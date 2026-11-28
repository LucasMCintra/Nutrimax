"""add meal image hash

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("meals", sa.Column("image_hash", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("meals", "image_hash")
