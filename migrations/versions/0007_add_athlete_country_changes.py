"""add athlete country changes

Revision ID: 0007_add_athlete_country_changes
Revises: 0006_import_created_notifications
Create Date: 2026-06-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_add_athlete_country_changes"
down_revision: Union[str, None] = "0006_import_created_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "athlete_country_changes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("athlete_id", sa.Integer(), nullable=False),
        sa.Column("from_country", sa.String(length=100), nullable=True),
        sa.Column("to_country", sa.String(length=100), nullable=False),
        sa.Column("change_year", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "change_year >= 1900 AND change_year <= 2100",
            name="ck_athlete_country_changes_year_valid",
        ),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "athlete_id",
            "from_country",
            "to_country",
            "change_year",
            name="uq_athlete_country_change",
        ),
    )
    op.create_index(op.f("ix_athlete_country_changes_athlete_id"), "athlete_country_changes", ["athlete_id"], unique=False)
    op.create_index(op.f("ix_athlete_country_changes_id"), "athlete_country_changes", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_athlete_country_changes_id"), table_name="athlete_country_changes")
    op.drop_index(op.f("ix_athlete_country_changes_athlete_id"), table_name="athlete_country_changes")
    op.drop_table("athlete_country_changes")
