"""add audit log review status

Revision ID: 0036_add_audit_log_review_status
Revises: 0035_cleanup_residual_event_levels
Create Date: 2026-08-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0036_add_audit_log_review_status"
down_revision: Union[str, None] = "0035_cleanup_residual_event_levels"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    columns = column_names("audit_logs")
    if not columns:
        return

    bind = op.get_bind()
    review_status_type = sa.String(length=20)
    if bind.dialect.name == "postgresql":
        review_status_type = sa.Enum(
            "PENDING",
            "APPROVED",
            "REVERTED",
            name="auditreviewstatusenum",
        )
        review_status_type.create(bind, checkfirst=True)

    with op.batch_alter_table("audit_logs") as batch_op:
        if "review_status" not in columns:
            batch_op.add_column(
                sa.Column(
                    "review_status",
                    review_status_type,
                    nullable=False,
                    server_default="APPROVED",
                )
            )
            batch_op.create_index("ix_audit_logs_review_status", ["review_status"])
        if "reviewed_by_super_admin_id" not in columns:
            batch_op.add_column(sa.Column("reviewed_by_super_admin_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_audit_logs_reviewed_by_super_admin_id_users",
                "users",
                ["reviewed_by_super_admin_id"],
                ["id"],
                ondelete="SET NULL",
            )
            batch_op.create_index(
                "ix_audit_logs_reviewed_by_super_admin_id",
                ["reviewed_by_super_admin_id"],
            )
        if "reviewed_at" not in columns:
            batch_op.add_column(sa.Column("reviewed_at", sa.DateTime(), nullable=True))
        if "review_note" not in columns:
            batch_op.add_column(sa.Column("review_note", sa.Text(), nullable=True))


def downgrade() -> None:
    columns = column_names("audit_logs")
    if not columns:
        return

    with op.batch_alter_table("audit_logs") as batch_op:
        if "review_note" in columns:
            batch_op.drop_column("review_note")
        if "reviewed_at" in columns:
            batch_op.drop_column("reviewed_at")
        if "reviewed_by_super_admin_id" in columns:
            batch_op.drop_index("ix_audit_logs_reviewed_by_super_admin_id")
            batch_op.drop_constraint("fk_audit_logs_reviewed_by_super_admin_id_users", type_="foreignkey")
            batch_op.drop_column("reviewed_by_super_admin_id")
        if "review_status" in columns:
            batch_op.drop_index("ix_audit_logs_review_status")
            batch_op.drop_column("review_status")

    if op.get_bind().dialect.name == "postgresql":
        sa.Enum(
            "PENDING",
            "APPROVED",
            "REVERTED",
            name="auditreviewstatusenum",
        ).drop(op.get_bind(), checkfirst=True)
