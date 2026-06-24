"""add vault attempt order uncertainty flag

Revision ID: 0023_add_vault_attempt_order_uncertain
Revises: 0022_security_audit_soft_delete
Create Date: 2026-06-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0023_add_vault_attempt_order_uncertain"
down_revision: Union[str, None] = "0022_security_audit_soft_delete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("results") as batch_op:
        batch_op.add_column(
            sa.Column(
                "vault_attempt_order_uncertain",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("results") as batch_op:
        batch_op.drop_column("vault_attempt_order_uncertain")
