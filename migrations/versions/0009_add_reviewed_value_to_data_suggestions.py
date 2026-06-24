"""add reviewed value to data suggestions

Revision ID: 0009_add_reviewed_value_to_data_suggestions
Revises: 0008_add_data_suggestions
Create Date: 2026-06-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_add_reviewed_value_to_data_suggestions"
down_revision: Union[str, None] = "0008_add_data_suggestions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("data_suggestions", sa.Column("reviewed_value", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("data_suggestions", "reviewed_value")
