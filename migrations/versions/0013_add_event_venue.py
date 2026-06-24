"""add event venue

Revision ID: 0013_add_event_venue
Revises: 0012_add_world_gymnastics_event_fields
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0013_add_event_venue"
down_revision: Union[str, None] = "0012_add_world_gymnastics_event_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if "venue" not in table_columns("events"):
        with op.batch_alter_table("events") as batch_op:
            batch_op.add_column(sa.Column("venue", sa.String(length=255), nullable=True))


def downgrade() -> None:
    if "venue" in table_columns("events"):
        with op.batch_alter_table("events") as batch_op:
            batch_op.drop_column("venue")
