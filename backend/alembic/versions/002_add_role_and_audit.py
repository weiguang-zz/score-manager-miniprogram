"""add role and audit fields

Revision ID: 002
Revises: 001
Create Date: 2026-03-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(20), nullable=False, server_default="admin"))
    op.add_column("users", sa.Column("admin_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("score_records", sa.Column("operator_id", sa.Integer(), nullable=True))
    op.add_column("score_records", sa.Column("operator_name", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("score_records", "operator_name")
    op.drop_column("score_records", "operator_id")
    op.drop_column("users", "admin_id")
    op.drop_column("users", "role")
