"""repair verified athlete audit metadata

Revision ID: 0039_repair_verified_athlete_audit
Revises: 0038_backfill_verified_athlete_profiles
Create Date: 2026-09-21
"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0039_repair_verified_athlete_audit"
down_revision: Union[str, None] = "0038_backfill_verified_athlete_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if not {"athletes", "audit_logs"}.issubset(inspector.get_table_names()):
        return

    inconsistent_athletes = connection.execute(
        sa.text(
            """
            SELECT id
            FROM athletes
            WHERE is_profile_verified = true
              AND (
                world_gymnastics_verified_at IS NULL
                OR world_gymnastics_verified_by_admin_id IS NULL
              )
            """
        )
    ).mappings()

    for athlete in inconsistent_athletes:
        audit_rows = connection.execute(
            sa.text(
                """
                SELECT admin_id, before_json, after_json, created_at
                FROM audit_logs
                WHERE entity_type = 'Athlete'
                  AND entity_id = :athlete_id
                  AND admin_id IS NOT NULL
                ORDER BY id DESC
                """
            ),
            {"athlete_id": athlete["id"]},
        ).mappings()
        for audit_row in audit_rows:
            try:
                before = json.loads(audit_row["before_json"] or "{}")
                after = json.loads(audit_row["after_json"] or "{}")
            except (TypeError, json.JSONDecodeError):
                continue
            if before.get("is_profile_verified") is not False or after.get("is_profile_verified") is not True:
                continue
            connection.execute(
                sa.text(
                    """
                    UPDATE athletes
                    SET world_gymnastics_verified_at = COALESCE(
                          world_gymnastics_verified_at,
                          :verified_at
                        ),
                        world_gymnastics_verified_by_admin_id = COALESCE(
                          world_gymnastics_verified_by_admin_id,
                          :admin_id
                        )
                    WHERE id = :athlete_id
                      AND is_profile_verified = true
                    """
                ),
                {
                    "athlete_id": athlete["id"],
                    "verified_at": audit_row["created_at"],
                    "admin_id": audit_row["admin_id"],
                },
            )
            break


def downgrade() -> None:
    # Restored metadata comes from immutable audit evidence and must not be erased.
    pass
