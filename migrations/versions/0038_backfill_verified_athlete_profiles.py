"""backfill verified athlete profiles

Revision ID: 0038_backfill_verified_athlete_profiles
Revises: 0037_add_athlete_profile_verification
Create Date: 2026-09-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0038_backfill_verified_athlete_profiles"
down_revision: Union[str, None] = "0037_add_athlete_profile_verification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    required_columns = {
        "is_profile_verified",
        "world_gymnastics_profile_url",
        "world_gymnastics_verified_at",
        "world_gymnastics_verified_by_admin_id",
    }
    if not required_columns.issubset(column_names("athletes")):
        return

    op.get_bind().execute(
        sa.text(
            """
            UPDATE athletes
            SET is_profile_verified = true
            WHERE is_profile_verified = false
              AND world_gymnastics_profile_url IS NOT NULL
              AND world_gymnastics_profile_url != ''
              AND world_gymnastics_verified_at IS NOT NULL
              AND world_gymnastics_verified_by_admin_id IS NOT NULL
              AND is_deleted = false
            """
        )
    )


def downgrade() -> None:
    # The backfill reflects prior verified admin decisions. Downgrading must not
    # erase certifications that may also have been confirmed after this migration.
    pass
