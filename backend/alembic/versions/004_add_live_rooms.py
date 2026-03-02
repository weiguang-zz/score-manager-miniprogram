"""add live rooms

Revision ID: 004
Revises: 003
Create Date: 2026-03-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "live_rooms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("score_records", sa.Column("room_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_score_records_room_id", "score_records", "live_rooms", ["room_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_score_records_room_id", "score_records", type_="foreignkey")
    op.drop_column("score_records", "room_id")
    op.drop_table("live_rooms")
