"""add event results reminder notification type

Revision ID: 0021_add_event_results_reminder_notification
Revises: 0020_add_data_entry_summary_notification
Create Date: 2026-06-10
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0021_add_event_results_reminder_notification"
down_revision: Union[str, None] = "0020_add_data_entry_summary_notification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'EVENT_RESULTS_REMINDER'")


def downgrade() -> None:
    pass
