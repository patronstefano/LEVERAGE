"""add event calendar entries

Revision ID: 0029_add_event_calendar_entries
Revises: 0028_add_user_preferred_language
Create Date: 2026-07-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0029_add_event_calendar_entries"
down_revision: Union[str, None] = "0028_add_user_preferred_language"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def existing_index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def existing_unique_constraint_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {
        constraint["name"]
        for constraint in inspector.get_unique_constraints(table_name)
        if constraint.get("name")
    }


def upgrade() -> None:
    if not has_table("event_calendar_entries"):
        op.create_table(
            "event_calendar_entries",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("event_id", sa.Integer(), nullable=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=False),
            sa.Column("year", sa.Integer(), nullable=False),
            sa.Column("discipline", sa.Enum("MAG", "WAG", "MAG_AND_WAG", name="eventdisciplineenum"), nullable=True),
            sa.Column("source", sa.String(length=100), nullable=False, server_default="gymternet_calendar"),
            sa.Column("source_row", sa.Integer(), nullable=True),
            sa.Column("source_note", sa.Text(), nullable=True),
            sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.CheckConstraint("end_date >= start_date", name="ck_event_calendar_entries_date_order"),
            sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )

    indexes = existing_index_names("event_calendar_entries")
    if "ix_event_calendar_entries_calendar" not in indexes:
        op.create_index(
            "ix_event_calendar_entries_calendar",
            "event_calendar_entries",
            ["is_deleted", "start_date", "year"],
            unique=False,
        )
    if "ix_event_calendar_entries_event" not in indexes:
        op.create_index(
            "ix_event_calendar_entries_event",
            "event_calendar_entries",
            ["event_id", "is_deleted"],
            unique=False,
        )

    constraints = existing_unique_constraint_names("event_calendar_entries")
    if "uq_event_calendar_entry_source" not in constraints:
        with op.batch_alter_table("event_calendar_entries") as batch_op:
            batch_op.create_unique_constraint(
                "uq_event_calendar_entry_source",
                ["source", "year", "source_row", "event_id", "name"],
            )


def downgrade() -> None:
    if has_table("event_calendar_entries"):
        op.drop_table("event_calendar_entries")
