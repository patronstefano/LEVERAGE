"""add athlete profile verification

Revision ID: 0037_add_athlete_profile_verification
Revises: 0036_add_audit_log_review_status
Create Date: 2026-09-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0037_add_athlete_profile_verification"
down_revision: Union[str, None] = "0036_add_audit_log_review_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    columns = column_names("athletes")
    if not columns or "is_profile_verified" in columns:
        return
    with op.batch_alter_table("athletes") as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_profile_verified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )


def downgrade() -> None:
    columns = column_names("athletes")
    if "is_profile_verified" not in columns:
        return
    with op.batch_alter_table("athletes") as batch_op:
        batch_op.drop_column("is_profile_verified")
