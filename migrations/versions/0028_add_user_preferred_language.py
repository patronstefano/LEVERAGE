"""add user preferred language

Revision ID: 0028_add_user_preferred_language
Revises: 0027_add_scalability_indexes
Create Date: 2026-06-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0028_add_user_preferred_language"
down_revision: Union[str, None] = "0027_add_scalability_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if has_column("users", "preferred_language"):
        return

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "preferred_language",
                sa.Enum("EN", "IT", "ES", "FR", name="languageenum"),
                nullable=False,
                server_default="EN",
            )
        )


def downgrade() -> None:
    if not has_column("users", "preferred_language"):
        return

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("preferred_language")
