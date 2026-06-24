"""security audit and soft delete

Revision ID: 0022_security_audit_soft_delete
Revises: 0021_add_event_results_reminder_notification
Create Date: 2026-06-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0022_security_audit_soft_delete"
down_revision: Union[str, None] = "0021_add_event_results_reminder_notification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def add_soft_delete_columns(table_name: str) -> None:
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.add_column(sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("deleted_by_admin_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            f"fk_{table_name}_deleted_by_admin_id_users",
            "users",
            ["deleted_by_admin_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(f"ix_{table_name}_is_deleted", ["is_deleted"])


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE roleenum ADD VALUE IF NOT EXISTS 'SUPER_ADMIN'")
        op.execute("ALTER TYPE notificationtypeenum ADD VALUE IF NOT EXISTS 'SECURITY_ALERT'")

    add_soft_delete_columns("athletes")
    add_soft_delete_columns("events")
    add_soft_delete_columns("results")

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("action", sa.String(length=50), nullable=False, index=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False, index=True),
        sa.Column("entity_id", sa.Integer(), nullable=True, index=True),
        sa.Column("before_json", sa.Text(), nullable=True),
        sa.Column("after_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, index=True),
    )

    if bind.dialect.name == "postgresql":
        op.execute(
            """
            UPDATE users
            SET role = 'SUPER_ADMIN'
            WHERE id = (
                SELECT id FROM users
                WHERE role::text = 'ADMIN'
                ORDER BY created_at ASC, id ASC
                LIMIT 1
            )
            AND NOT EXISTS (
                SELECT 1 FROM users WHERE role::text = 'SUPER_ADMIN'
            )
            """
        )
    else:
        op.execute(
            """
            UPDATE users
            SET role = 'SUPER_ADMIN'
            WHERE id = (
                SELECT id FROM users
                WHERE role = 'ADMIN'
                ORDER BY created_at ASC, id ASC
                LIMIT 1
            )
            AND NOT EXISTS (
                SELECT 1 FROM users WHERE role = 'SUPER_ADMIN'
            )
            """
        )


def downgrade() -> None:
    op.drop_table("audit_logs")
    for table_name in ("results", "events", "athletes"):
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_index(f"ix_{table_name}_is_deleted")
            batch_op.drop_constraint(f"fk_{table_name}_deleted_by_admin_id_users", type_="foreignkey")
            batch_op.drop_column("deleted_by_admin_id")
            batch_op.drop_column("deleted_at")
            batch_op.drop_column("is_deleted")
