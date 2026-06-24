"""add scalability indexes

Revision ID: 0027_add_scalability_indexes
Revises: 0026_replace_passwordless_authentication
Create Date: 2026-06-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0027_add_scalability_indexes"
down_revision: Union[str, None] = "0026_replace_passwordless_authentication"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INDEXES = (
    ("athletes", "ix_athletes_lookup", ["is_deleted", "last_name", "first_name"]),
    ("athletes", "ix_athletes_country_discipline", ["is_deleted", "country", "discipline"]),
    ("events", "ix_events_calendar", ["is_deleted", "start_date", "year"]),
    ("events", "ix_events_year_level", ["is_deleted", "year", "level"]),
    ("events", "ix_events_domain", ["is_deleted", "discipline", "category", "level"]),
    (
        "results",
        "ix_results_event_rank_scope",
        ["event_id", "is_deleted", "format", "round", "discipline", "category", "apparatus", "day"],
    ),
    ("results", "ix_results_event_metric", ["event_id", "is_deleted", "rank", "score", "D_score"]),
    ("results", "ix_results_athlete_event_scope", ["athlete_id", "event_id", "is_deleted"]),
    (
        "results",
        "ix_results_athlete_timeline",
        ["athlete_id", "is_deleted", "apparatus", "format", "round", "day"],
    ),
    (
        "results",
        "ix_results_duplicate_lookup",
        ["athlete_id", "event_id", "apparatus", "vt_attempt", "day", "format", "round", "discipline", "category", "is_deleted"],
    ),
    ("results", "ix_results_country_scope", ["represented_country", "is_deleted"]),
)


def existing_index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    for table_name, index_name, columns in INDEXES:
        if index_name not in existing_index_names(table_name):
            op.create_index(index_name, table_name, columns, unique=False)


def downgrade() -> None:
    for table_name, index_name, _ in reversed(INDEXES):
        if index_name in existing_index_names(table_name):
            op.drop_index(index_name, table_name=table_name)
