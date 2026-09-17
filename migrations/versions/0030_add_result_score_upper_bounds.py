"""add result score upper bounds

Revision ID: 0030_add_result_score_upper_bounds
Revises: 0029_add_event_calendar_entries
Create Date: 2026-07-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0030_add_result_score_upper_bounds"
down_revision: Union[str, None] = "0029_add_event_calendar_entries"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def existing_check_constraint_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {
        constraint["name"]
        for constraint in inspector.get_check_constraints(table_name)
        if constraint.get("name")
    }


def upgrade() -> None:
    if not has_table("results"):
        return

    constraints = existing_check_constraint_names("results")
    with op.batch_alter_table("results") as batch_op:
        if "ck_results_non_aa_score_upper_bound" not in constraints:
            batch_op.create_check_constraint(
                "ck_results_non_aa_score_upper_bound",
                "score IS NULL OR apparatus = 'AA' OR score <= 20",
            )
        if "ck_results_d_score_upper_bound" not in constraints:
            batch_op.create_check_constraint(
                "ck_results_d_score_upper_bound",
                "D_score IS NULL OR D_score <= 10",
            )


def downgrade() -> None:
    if not has_table("results"):
        return

    constraints = existing_check_constraint_names("results")
    with op.batch_alter_table("results") as batch_op:
        if "ck_results_d_score_upper_bound" in constraints:
            batch_op.drop_constraint("ck_results_d_score_upper_bound", type_="check")
        if "ck_results_non_aa_score_upper_bound" in constraints:
            batch_op.drop_constraint("ck_results_non_aa_score_upper_bound", type_="check")
