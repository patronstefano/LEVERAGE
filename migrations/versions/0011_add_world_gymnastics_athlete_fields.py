"""add world gymnastics athlete fields

Revision ID: 0011_add_world_gymnastics_athlete_fields
Revises: 0010_replace_athlete_birth_year
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0011_add_world_gymnastics_athlete_fields"
down_revision: Union[str, None] = "0010_replace_athlete_birth_year"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    columns = table_columns("athletes")
    with op.batch_alter_table("athletes") as batch_op:
        if "world_gymnastics_athlete_id" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_athlete_id", sa.String(length=50), nullable=True))
        if "world_gymnastics_profile_url" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_profile_url", sa.String(length=500), nullable=True))
        if "world_gymnastics_status" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_status", sa.String(length=100), nullable=True))
        if "world_gymnastics_verified_at" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_verified_at", sa.DateTime(), nullable=True))
        if "world_gymnastics_verified_by_admin_id" not in columns:
            batch_op.add_column(sa.Column("world_gymnastics_verified_by_admin_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_athletes_world_gymnastics_verified_by_admin_id_users",
                "users",
                ["world_gymnastics_verified_by_admin_id"],
                ["id"],
                ondelete="SET NULL",
            )


def downgrade() -> None:
    columns = table_columns("athletes")
    with op.batch_alter_table("athletes") as batch_op:
        if "world_gymnastics_verified_by_admin_id" in columns:
            batch_op.drop_constraint(
                "fk_athletes_world_gymnastics_verified_by_admin_id_users",
                type_="foreignkey",
            )
            batch_op.drop_column("world_gymnastics_verified_by_admin_id")
        if "world_gymnastics_verified_at" in columns:
            batch_op.drop_column("world_gymnastics_verified_at")
        if "world_gymnastics_status" in columns:
            batch_op.drop_column("world_gymnastics_status")
        if "world_gymnastics_profile_url" in columns:
            batch_op.drop_column("world_gymnastics_profile_url")
        if "world_gymnastics_athlete_id" in columns:
            batch_op.drop_column("world_gymnastics_athlete_id")
