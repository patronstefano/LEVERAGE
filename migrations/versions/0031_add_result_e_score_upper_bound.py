"""add result e score upper bound

Revision ID: 0031_add_result_e_score_upper_bound
Revises: 0030_add_result_score_upper_bounds
Create Date: 2026-07-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0031_add_result_e_score_upper_bound"
down_revision: Union[str, None] = "0030_add_result_score_upper_bounds"
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
        if "ck_results_e_score_upper_bound" not in constraints:
            batch_op.create_check_constraint(
                "ck_results_e_score_upper_bound",
                "E_score IS NULL OR E_score <= 10",
            )


def downgrade() -> None:
    if not has_table("results"):
        return

    constraints = existing_check_constraint_names("results")
    with op.batch_alter_table("results") as batch_op:
        if "ck_results_e_score_upper_bound" in constraints:
            batch_op.drop_constraint("ck_results_e_score_upper_bound", type_="check")
