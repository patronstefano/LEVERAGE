"""add mixed team result format

Revision ID: 0033_add_mixed_team_result_format
Revises: 0032_add_result_apparatus_metric_index
Create Date: 2026-08-03
"""
from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0033_add_mixed_team_result_format"
down_revision: Union[str, None] = "0032_add_result_apparatus_metric_index"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def add_postgres_enum_value() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE formatenum ADD VALUE IF NOT EXISTS 'MIXED_TEAM'")


def first_event_id(name: str, year: int, *, include_deleted: bool = False) -> Optional[int]:
    deleted_clause = "" if include_deleted else " AND is_deleted = false"
    return op.get_bind().execute(
        sa.text(
            f"""
            SELECT id
            FROM events
            WHERE name = :name
              AND year = :year
              {deleted_clause}
            ORDER BY id
            LIMIT 1
            """
        ),
        {"name": name, "year": year},
    ).scalar()


def merge_mixed_team_event(
    source_name: str,
    target_name: str,
    year: int,
    *,
    unmatched_calendar_entry_names: Sequence[str] = (),
) -> None:
    tables = table_names()
    if "events" not in tables or "results" not in tables:
        return

    source_id = first_event_id(source_name, year, include_deleted=True)
    target_id = first_event_id(target_name, year)
    if source_id is None or target_id is None or source_id == target_id:
        return

    op.get_bind().execute(
        sa.text(
            """
            UPDATE results
            SET event_id = :target_id,
                format = 'MIXED_TEAM',
                round = 'FINAL'
            WHERE event_id = :source_id
            """
        ),
        {"source_id": source_id, "target_id": target_id},
    )

    if "event_calendar_entries" in tables:
        op.get_bind().execute(
            sa.text(
                """
                UPDATE event_calendar_entries
                SET event_id = :target_id,
                    name = :target_name
                WHERE event_id = :source_id
                """
            ),
            {"source_id": source_id, "target_id": target_id, "target_name": target_name},
        )
        for calendar_name in unmatched_calendar_entry_names:
            op.get_bind().execute(
                sa.text(
                    """
                    UPDATE event_calendar_entries
                    SET event_id = NULL,
                        source_note = 'left_unmatched_after_mt_merge'
                    WHERE event_id = :source_id
                      AND name = :calendar_name
                      AND year = :year
                    """
                ),
                {"source_id": source_id, "calendar_name": calendar_name, "year": year},
            )

    if "notifications" in tables:
        op.get_bind().execute(
            sa.text(
                """
                UPDATE notifications
                SET related_event_id = :target_id
                WHERE related_event_id = :source_id
                """
            ),
            {"source_id": source_id, "target_id": target_id},
        )

    if "saved_events" in tables:
        op.get_bind().execute(
            sa.text(
                """
                UPDATE saved_events
                SET event_id = :target_id
                WHERE event_id = :source_id
                  AND NOT EXISTS (
                    SELECT 1
                    FROM saved_events duplicate
                    WHERE duplicate.user_id = saved_events.user_id
                      AND duplicate.event_id = :target_id
                  )
                """
            ),
            {"source_id": source_id, "target_id": target_id},
        )

    if "result_entry_contexts" in tables:
        op.get_bind().execute(
            sa.text(
                """
                UPDATE result_entry_contexts
                SET event_id = :target_id,
                    format = 'MIXED_TEAM',
                    round = 'FINAL'
                WHERE event_id = :source_id
                  AND NOT EXISTS (
                    SELECT 1
                    FROM result_entry_contexts duplicate
                    WHERE duplicate.admin_id = result_entry_contexts.admin_id
                      AND duplicate.event_id = :target_id
                  )
                """
            ),
            {"source_id": source_id, "target_id": target_id},
        )

    if "data_suggestions" in tables:
        op.get_bind().execute(
            sa.text(
                """
                UPDATE data_suggestions
                SET entity_id = :target_id
                WHERE entity_id = :source_id
                  AND entity_type IN ('EVENT', 'event')
                """
            ),
            {"source_id": source_id, "target_id": target_id},
        )

    if "site_analytics_events" in tables:
        op.get_bind().execute(
            sa.text(
                """
                UPDATE site_analytics_events
                SET entity_id = :target_id
                WHERE entity_id = :source_id
                  AND entity_type = 'event'
                """
            ),
            {"source_id": source_id, "target_id": target_id},
        )

    op.get_bind().execute(
        sa.text(
            """
            UPDATE events
            SET is_deleted = true,
                deleted_at = CURRENT_TIMESTAMP
            WHERE id = :source_id
            """
        ),
        {"source_id": source_id},
    )


def upgrade() -> None:
    add_postgres_enum_value()
    merge_mixed_team_event("European Championships MT", "European Championships", 2025)
    merge_mixed_team_event(
        "Chinese Championships MT",
        "Chinese Championships",
        2026,
        unmatched_calendar_entry_names=("Chinese Junior Championships",),
    )


def downgrade() -> None:
    tables = table_names()
    if "events" not in tables or "results" not in tables:
        return

    source_id = first_event_id("European Championships MT", 2025, include_deleted=True)
    target_id = first_event_id("European Championships", 2025)
    if source_id is None or target_id is None or source_id == target_id:
        return

    op.get_bind().execute(
        sa.text("UPDATE events SET is_deleted = false, deleted_at = NULL WHERE id = :source_id"),
        {"source_id": source_id},
    )
    op.get_bind().execute(
        sa.text(
            """
            UPDATE results
            SET event_id = :source_id,
                format = 'INDIVIDUAL',
                round = 'FINAL'
            WHERE event_id = :target_id
              AND format = 'MIXED_TEAM'
            """
        ),
        {"source_id": source_id, "target_id": target_id},
    )
