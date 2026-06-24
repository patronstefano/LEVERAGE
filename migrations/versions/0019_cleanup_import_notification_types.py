"""cleanup import notification types

Revision ID: 0019_cleanup_import_notification_types
Revises: 0018_add_import_summary_notification
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0019_cleanup_import_notification_types"
down_revision: Union[str, None] = "0018_add_import_summary_notification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OLD_IMPORT_NOTIFICATION_TYPES = (
    "IMPORT_CREATED_ATHLETE",
    "IMPORT_CREATED_EVENT",
    "import_created_athlete",
    "import_created_event",
)


def upgrade() -> None:
    bind = op.get_bind()
    values = ", ".join(f"'{value}'" for value in OLD_IMPORT_NOTIFICATION_TYPES)
    if bind.dialect.name == "postgresql":
        op.execute(
            f"""
            UPDATE notifications
            SET type = 'IMPORT_SUMMARY'
            WHERE type::text IN ({values})
            """
        )
    else:
        op.execute(
            f"""
            UPDATE notifications
            SET type = 'IMPORT_SUMMARY'
            WHERE type IN ({values})
            """
        )


def downgrade() -> None:
    pass
