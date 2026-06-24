"""result category and event domain updates

Revision ID: 0002_result_category_and_event_domain_updates
Revises: 0001_initial
Create Date: 2026-05-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_result_category_and_event_domain_updates"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


old_event_discipline_enum = sa.Enum("MAG", "WAG", "BOTH", name="eventdisciplineenum")
new_event_discipline_enum = sa.Enum("MAG", "WAG", "MAG_AND_WAG", name="eventdisciplineenum")
old_category_enum = sa.Enum("JUNIOR", "SENIOR", name="categoryenum")
new_category_enum = sa.Enum("JUNIOR", "SENIOR", "JUNIOR_AND_SENIOR", name="categoryenum")


def upgrade() -> None:
    op.execute("UPDATE events SET discipline = 'MAG_AND_WAG' WHERE discipline = 'BOTH'")

    with op.batch_alter_table("athletes") as batch_op:
        batch_op.drop_column("status")

    with op.batch_alter_table("events") as batch_op:
        batch_op.alter_column(
            "discipline",
            existing_type=old_event_discipline_enum,
            type_=new_event_discipline_enum,
            existing_nullable=False,
        )
        batch_op.alter_column(
            "category",
            existing_type=old_category_enum,
            type_=new_category_enum,
            existing_nullable=False,
        )

    with op.batch_alter_table("results") as batch_op:
        batch_op.add_column(sa.Column("category", new_category_enum, nullable=True))

    op.execute(
        """
        UPDATE results
        SET category = (
            SELECT events.category
            FROM events
            WHERE events.id = results.event_id
        )
        """
    )

    with op.batch_alter_table("results") as batch_op:
        batch_op.alter_column(
            "category",
            existing_type=new_category_enum,
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("results") as batch_op:
        batch_op.drop_column("category")

    with op.batch_alter_table("events") as batch_op:
        batch_op.alter_column(
            "category",
            existing_type=new_category_enum,
            type_=old_category_enum,
            existing_nullable=False,
        )
        batch_op.alter_column(
            "discipline",
            existing_type=new_event_discipline_enum,
            type_=old_event_discipline_enum,
            existing_nullable=False,
        )

    op.execute("UPDATE events SET discipline = 'BOTH' WHERE discipline = 'MAG_AND_WAG'")

    with op.batch_alter_table("athletes") as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                sa.Enum("ACTIVE", "RETIRED", name="statusenum"),
                nullable=False,
                server_default="ACTIVE",
            )
        )
