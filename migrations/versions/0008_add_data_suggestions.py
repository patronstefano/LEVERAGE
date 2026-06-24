"""add data suggestions

Revision ID: 0008_add_data_suggestions
Revises: 0007_add_athlete_country_changes
Create Date: 2026-06-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_add_data_suggestions"
down_revision: Union[str, None] = "0007_add_athlete_country_changes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_suggestions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.Enum("ATHLETE", "EVENT", name="datasuggestionentitytypeenum"), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("suggested_value", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("source_title", sa.String(length=255), nullable=True),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "ACCEPTED", "EDITED", "REJECTED", name="datasuggestionstatusenum"), nullable=False),
        sa.Column("created_by_admin_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_by_admin_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_data_suggestions_confidence_range",
        ),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reviewed_by_admin_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_data_suggestions_entity_id"), "data_suggestions", ["entity_id"], unique=False)
    op.create_index(op.f("ix_data_suggestions_entity_type"), "data_suggestions", ["entity_type"], unique=False)
    op.create_index(op.f("ix_data_suggestions_field_name"), "data_suggestions", ["field_name"], unique=False)
    op.create_index(op.f("ix_data_suggestions_id"), "data_suggestions", ["id"], unique=False)
    op.create_index(op.f("ix_data_suggestions_status"), "data_suggestions", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_data_suggestions_status"), table_name="data_suggestions")
    op.drop_index(op.f("ix_data_suggestions_id"), table_name="data_suggestions")
    op.drop_index(op.f("ix_data_suggestions_field_name"), table_name="data_suggestions")
    op.drop_index(op.f("ix_data_suggestions_entity_type"), table_name="data_suggestions")
    op.drop_index(op.f("ix_data_suggestions_entity_id"), table_name="data_suggestions")
    op.drop_table("data_suggestions")
