"""add format to result entry context

Revision ID: 0004_add_format_to_result_entry_context
Revises: 0003_split_event_and_result_category_enums
Create Date: 2026-05-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_add_format_to_result_entry_context"
down_revision: Union[str, None] = "0003_split_event_and_result_category_enums"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


format_enum = sa.Enum("TEAM", "INDIVIDUAL", "APPARATUS", name="formatenum")


def upgrade() -> None:
    with op.batch_alter_table("result_entry_contexts") as batch_op:
        batch_op.add_column(sa.Column("format", format_enum, nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("result_entry_contexts") as batch_op:
        batch_op.drop_column("format")
