"""add site analytics events

Revision ID: 0015_add_site_analytics_events
Revises: 0014_add_saved_dashboard_views
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0015_add_site_analytics_events"
down_revision: Union[str, None] = "0014_add_saved_dashboard_views"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if has_table("site_analytics_events"):
        return

    op.create_table(
        "site_analytics_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "PAGE_VIEW",
                "SEARCH",
                "ATHLETE_VIEW",
                "EVENT_VIEW",
                "DASHBOARD_VIEW",
                "SESSION_END",
                name="siteanalyticseventtypeenum",
            ),
            nullable=False,
        ),
        sa.Column("visitor_id", sa.String(length=100), nullable=True),
        sa.Column("session_id", sa.String(length=100), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("path", sa.String(length=500), nullable=True),
        sa.Column("search_query", sa.String(length=255), nullable=True),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_site_analytics_events_id"), "site_analytics_events", ["id"], unique=False)
    op.create_index(op.f("ix_site_analytics_events_event_type"), "site_analytics_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_site_analytics_events_visitor_id"), "site_analytics_events", ["visitor_id"], unique=False)
    op.create_index(op.f("ix_site_analytics_events_session_id"), "site_analytics_events", ["session_id"], unique=False)
    op.create_index(op.f("ix_site_analytics_events_user_id"), "site_analytics_events", ["user_id"], unique=False)
    op.create_index(op.f("ix_site_analytics_events_created_at"), "site_analytics_events", ["created_at"], unique=False)


def downgrade() -> None:
    if not has_table("site_analytics_events"):
        return

    op.drop_index(op.f("ix_site_analytics_events_created_at"), table_name="site_analytics_events")
    op.drop_index(op.f("ix_site_analytics_events_user_id"), table_name="site_analytics_events")
    op.drop_index(op.f("ix_site_analytics_events_session_id"), table_name="site_analytics_events")
    op.drop_index(op.f("ix_site_analytics_events_visitor_id"), table_name="site_analytics_events")
    op.drop_index(op.f("ix_site_analytics_events_event_type"), table_name="site_analytics_events")
    op.drop_index(op.f("ix_site_analytics_events_id"), table_name="site_analytics_events")
    op.drop_table("site_analytics_events")
