"""add data entry summary notification type

Revision ID: 0020_add_data_entry_summary_notification
Revises: 0019_cleanup_import_notification_types
Create Date: 2026-06-10
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0020_add_data_entry_summary_notification"
down_revision: Union[str, None] = "0019_cleanup_import_notification_types"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'DATA_ENTRY_SUMMARY'")


def downgrade() -> None:
    pass
