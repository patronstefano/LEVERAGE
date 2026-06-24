"""add admin promotion notification type

Revision ID: 0016_add_admin_promotion_notification
Revises: 0015_add_site_analytics_events
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0016_add_admin_promotion_notification"
down_revision: Union[str, None] = "0015_add_site_analytics_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'ADMIN_PROMOTION'")


def downgrade() -> None:
    pass
