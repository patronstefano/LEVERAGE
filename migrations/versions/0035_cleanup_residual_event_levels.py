"""cleanup residual event levels

Revision ID: 0035_cleanup_residual_event_levels
Revises: 0034_reclassify_domestic_event_levels
Create Date: 2026-08-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0035_cleanup_residual_event_levels"
down_revision: Union[str, None] = "0034_reclassify_domestic_event_levels"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    if "events" not in table_names():
        return

    op.get_bind().execute(
        sa.text(
            """
            UPDATE events
            SET name = :new_name,
                level = 'NATIONAL_EVENT'
            WHERE name = :old_name
              AND is_deleted = false
            """
        ),
        {"old_name": "1st Bundlesiga League 2", "new_name": "1st Bundesliga League 2"},
    )
    op.get_bind().execute(
        sa.text(
            """
            UPDATE events
            SET name = :new_name,
                level = 'NATIONAL_EVENT'
            WHERE name = :old_name
              AND is_deleted = false
            """
        ),
        {"old_name": "2nd Bundlesiga League 2", "new_name": "2nd Bundesliga League 2"},
    )
    op.get_bind().execute(
        sa.text(
            """
            UPDATE events
            SET name = :new_name,
                level = 'NATIONAL_EVENT'
            WHERE name = :old_name
              AND is_deleted = false
            """
        ),
        {"old_name": "Japanese National Spots Festival", "new_name": "Japanese National Sports Festival"},
    )
    op.get_bind().execute(
        sa.text(
            """
            UPDATE events
            SET level = 'CONTINENTAL_CHAMPIONSHIPS'
            WHERE name IN (
                'Asian Junior Championships',
                'Junior Pan Am Championships',
                'Junior Pan American Championships',
                'Oceania Championships'
            )
              AND level = 'INTERNATIONAL_EVENT'
              AND is_deleted = false
            """
        )
    )


def downgrade() -> None:
    # Data-level downgrade intentionally left non-destructive.
    return
