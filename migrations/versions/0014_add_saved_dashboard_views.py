"""add saved dashboard views

Revision ID: 0014_add_saved_dashboard_views
Revises: 0013_add_event_venue
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0014_add_saved_dashboard_views"
down_revision: Union[str, None] = "0013_add_event_venue"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if has_table("saved_dashboard_views"):
        return

    op.create_table(
        "saved_dashboard_views",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("view_type", sa.String(length=50), nullable=False),
        sa.Column("chart_type", sa.String(length=50), nullable=True),
        sa.Column("metric", sa.String(length=20), nullable=True),
        sa.Column("filters_json", sa.Text(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_saved_dashboard_views_user_name"),
    )
    op.create_index(op.f("ix_saved_dashboard_views_id"), "saved_dashboard_views", ["id"], unique=False)
    op.create_index(op.f("ix_saved_dashboard_views_user_id"), "saved_dashboard_views", ["user_id"], unique=False)


def downgrade() -> None:
    if not has_table("saved_dashboard_views"):
        return

    op.drop_index(op.f("ix_saved_dashboard_views_user_id"), table_name="saved_dashboard_views")
    op.drop_index(op.f("ix_saved_dashboard_views_id"), table_name="saved_dashboard_views")
    op.drop_table("saved_dashboard_views")
