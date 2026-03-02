"""init admin users

Revision ID: 003
Revises: 002
Create Date: 2026-03-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set all existing users to admin role (in case server_default didn't apply to existing rows)
    op.execute("UPDATE users SET role = 'admin' WHERE role IS NULL OR role = ''")


def downgrade() -> None:
    pass
