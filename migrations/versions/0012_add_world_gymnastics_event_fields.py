"""add world gymnastics event fields

Revision ID: 0012_add_world_gymnastics_event_fields
Revises: 0011_add_world_gymnastics_athlete_fields
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0012_add_world_gymnastics_event_fields"
down_revision: Union[str, None] = "0011_add_world_gymnastics_athlete_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    columns = table_columns("events")
    with op.batch_alter_table("events") as batch_op:
        if "world_gymnastics_event_id" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_event_id", sa.String(length=50), nullable=True))
        if "world_gymnastics_event_url" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_event_url", sa.String(length=500), nullable=True))
        if "world_gymnastics_status" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_status", sa.String(length=100), nullable=True))
        if "world_gymnastics_verified_at" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_verified_at", sa.DateTime(), nullable=True))
        if "world_gymnastics_verified_by_admin_id" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_verified_by_admin_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_events_world_gymnastics_verified_by_admin_id_users",
                "users",
                ["world_gymnastics_verified_by_admin_id"],
                ["id"],
                ondelete="SET NULL",
            )


def downgrade() -> None:
    columns = table_columns("events")
    with op.batch_alter_table("events") as batch_op:
        if "world_gymnastics_verified_by_admin_id" in columns:
            batch_op.drop_constraint(
                "fk_events_world_gymnastics_verified_by_admin_id_users",
                type_="foreignkey",
            )
            batch_op.drop_column("world_gymnastics_verified_by_admin_id")
        if "world_gymnastics_verified_at" in columns:
            batch_op.drop_column("world_gymnastics_verified_at")
        if "world_gymnastics_status" in columns:
            batch_op.drop_column("world_gymnastics_status")
        if "world_gymnastics_event_url" in columns:
            batch_op.drop_column("world_gymnastics_event_url")
        if "world_gymnastics_event_id" in columns:
            batch_op.drop_column("world_gymnastics_event_id")
