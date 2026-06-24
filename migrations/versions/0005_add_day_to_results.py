"""add day to results

Revision ID: 0005_add_day_to_results
Revises: 0004_add_format_to_result_entry_context
Create Date: 2026-06-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_add_day_to_results"
down_revision: Union[str, None] = "0004_add_format_to_result_entry_context"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("results") as batch_op:
        batch_op.add_column(sa.Column("day", sa.Integer(), nullable=True))
        batch_op.create_check_constraint(
            "ck_results_day_positive",
            "day IS NULL OR day >= 1",
        )

    with op.batch_alter_table("result_entry_contexts") as batch_op:
        batch_op.add_column(sa.Column("day", sa.Integer(), nullable=True))
        batch_op.create_check_constraint(
            "ck_result_entry_contexts_day_positive",
            "day IS NULL OR day >= 1",
        )


def downgrade() -> None:
    with op.batch_alter_table("result_entry_contexts") as batch_op:
        batch_op.drop_constraint("ck_result_entry_contexts_day_positive", type_="check")
        batch_op.drop_column("day")

    with op.batch_alter_table("results") as batch_op:
        batch_op.drop_constraint("ck_results_day_positive", type_="check")
        batch_op.drop_column("day")
