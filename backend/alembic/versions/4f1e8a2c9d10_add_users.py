"""add users

Revision ID: 4f1e8a2c9d10
Revises: 9552323c74d8

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4f1e8a2c9d10"
down_revision: Union[str, None] = "9552323c74d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.add_column("clients", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_clients_user_id", "clients", ["user_id"])
    op.create_foreign_key("fk_clients_user_id", "clients", "users", ["user_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_clients_user_id", "clients", type_="foreignkey")
    op.drop_constraint("uq_clients_user_id", "clients", type_="unique")
    op.drop_column("clients", "user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
