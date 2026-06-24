"""add import summary notification type

Revision ID: 0018_add_import_summary_notification
Revises: 0017_add_admin_demotion_notification
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0018_add_import_summary_notification"
down_revision: Union[str, None] = "0017_add_admin_demotion_notification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'IMPORT_SUMMARY'")


def downgrade() -> None:
    pass
