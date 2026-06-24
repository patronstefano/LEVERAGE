"""legacy import notification migration

Revision ID: 0006_import_created_notifications
Revises: 0005_add_day_to_results
Create Date: 2026-06-03
"""
from typing import Sequence, Union

revision: str = "0006_import_created_notifications"
down_revision: Union[str, None] = "0005_add_day_to_results"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
