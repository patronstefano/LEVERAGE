"""split event and result category enums

Revision ID: 0003_split_event_and_result_category_enums
Revises: 0002_result_category_and_event_domain_updates
Create Date: 2026-05-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_split_event_and_result_category_enums"
down_revision: Union[str, None] = "0002_result_category_and_event_domain_updates"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


legacy_category_enum = sa.Enum("JUNIOR", "SENIOR", "JUNIOR_AND_SENIOR", name="categoryenum")
event_category_enum = sa.Enum("JUNIOR", "SENIOR", "JUNIOR_AND_SENIOR", name="eventcategoryenum")
result_category_enum = sa.Enum("JUNIOR", "SENIOR", name="resultcategoryenum")


def upgrade() -> None:
    invalid_result_categories = op.get_bind().execute(
        sa.text("SELECT COUNT(*) FROM results WHERE category = 'JUNIOR_AND_SENIOR'")
    ).scalar()
    if invalid_result_categories:
        raise RuntimeError(
            "Cannot split result category enum while results.category contains JUNIOR_AND_SENIOR. "
            "Set each affected result to JUNIOR or SENIOR before upgrading."
        )

    with op.batch_alter_table("events") as batch_op:
        batch_op.alter_column(
            "category",
            existing_type=legacy_category_enum,
            type_=event_category_enum,
            existing_nullable=False,
        )

    with op.batch_alter_table("results") as batch_op:
        batch_op.alter_column(
            "category",
            existing_type=legacy_category_enum,
            type_=result_category_enum,
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("results") as batch_op:
        batch_op.alter_column(
            "category",
            existing_type=result_category_enum,
            type_=legacy_category_enum,
            existing_nullable=False,
        )

    with op.batch_alter_table("events") as batch_op:
        batch_op.alter_column(
            "category",
            existing_type=event_category_enum,
            type_=legacy_category_enum,
            existing_nullable=False,
        )
