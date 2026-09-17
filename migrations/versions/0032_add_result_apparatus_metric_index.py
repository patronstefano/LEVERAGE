"""add result apparatus metric index

Revision ID: 0032_add_result_apparatus_metric_index
Revises: 0031_add_result_e_score_upper_bound
Create Date: 2026-07-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0032_add_result_apparatus_metric_index"
down_revision: Union[str, None] = "0031_add_result_e_score_upper_bound"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INDEX_NAME = "ix_results_apparatus_metric_scope"
INDEX_COLUMNS = [
    "is_deleted",
    "apparatus",
    "discipline",
    "event_id",
    "athlete_id",
    "category",
    "format",
    "round",
    "day",
    "D_score",
    "score",
]


def has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def existing_index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {
        index["name"]
        for index in inspector.get_indexes(table_name)
        if index.get("name")
    }


def upgrade() -> None:
    if not has_table("results"):
        return

    if INDEX_NAME not in existing_index_names("results"):
        op.create_index(INDEX_NAME, "results", INDEX_COLUMNS, unique=False)


def downgrade() -> None:
    if not has_table("results"):
        return

    if INDEX_NAME in existing_index_names("results"):
        op.drop_index(INDEX_NAME, table_name="results")
