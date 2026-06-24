"""add result represented country

Revision ID: 0025_add_result_represented_country
Revises: 0024_allow_nullable_result_score
Create Date: 2026-06-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0025_add_result_represented_country"
down_revision: Union[str, None] = "0024_allow_nullable_result_score"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("results") as batch_op:
        batch_op.add_column(sa.Column("represented_country", sa.String(length=100), nullable=True))
        batch_op.create_index(
            "ix_results_represented_country",
            ["represented_country"],
            unique=False,
        )

    op.execute(
        """
        UPDATE results
        SET represented_country = (
            SELECT athletes.country
            FROM athletes
            WHERE athletes.id = results.athlete_id
        )
        WHERE represented_country IS NULL
        """
    )


def downgrade() -> None:
    with op.batch_alter_table("results") as batch_op:
        batch_op.drop_index("ix_results_represented_country")
        batch_op.drop_column("represented_country")
