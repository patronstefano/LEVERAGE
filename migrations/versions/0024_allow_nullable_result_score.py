"""allow nullable result score

Revision ID: 0024_allow_nullable_result_score
Revises: 0023_add_vault_attempt_order_uncertain
Create Date: 2026-06-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0024_allow_nullable_result_score"
down_revision: Union[str, None] = "0023_add_vault_attempt_order_uncertain"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    with op.batch_alter_table("results") as batch_op:
        if bind.dialect.name != "sqlite":
            batch_op.drop_constraint("ck_results_score_non_negative", type_="check")
        batch_op.alter_column("score", existing_type=sa.Float(), nullable=True)
        batch_op.create_check_constraint(
            "ck_results_score_non_negative",
            "score IS NULL OR score >= 0",
        )


def downgrade() -> None:
    bind = op.get_bind()
    with op.batch_alter_table("results") as batch_op:
        if bind.dialect.name != "sqlite":
            batch_op.drop_constraint("ck_results_score_non_negative", type_="check")
        batch_op.alter_column("score", existing_type=sa.Float(), nullable=False)
        batch_op.create_check_constraint(
            "ck_results_score_non_negative",
            "score >= 0",
        )
