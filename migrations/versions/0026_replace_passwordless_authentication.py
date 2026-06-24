"""replace passwordless authentication

Revision ID: 0026_replace_passwordless_authentication
Revises: 0025_add_result_represented_country
Create Date: 2026-06-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0026_replace_passwordless_authentication"
down_revision: Union[str, None] = "0025_add_result_represented_country"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_COLUMNS = {
    "password_hash": sa.Column("password_hash", sa.String(length=255), nullable=True),
    "email_verification_token_hash": sa.Column("email_verification_token_hash", sa.String(length=64), nullable=True),
    "email_verification_expires_at": sa.Column("email_verification_expires_at", sa.DateTime(), nullable=True),
    "email_verification_sent_at": sa.Column("email_verification_sent_at", sa.DateTime(), nullable=True),
    "password_reset_token_hash": sa.Column("password_reset_token_hash", sa.String(length=64), nullable=True),
    "password_reset_expires_at": sa.Column("password_reset_expires_at", sa.DateTime(), nullable=True),
    "password_reset_sent_at": sa.Column("password_reset_sent_at", sa.DateTime(), nullable=True),
    "failed_login_attempts": sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
    "login_locked_until": sa.Column("login_locked_until", sa.DateTime(), nullable=True),
    "auth_version": sa.Column("auth_version", sa.Integer(), nullable=False, server_default="1"),
    "mfa_secret": sa.Column("mfa_secret", sa.String(length=64), nullable=True),
    "mfa_enabled": sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    "mfa_recovery_codes": sa.Column("mfa_recovery_codes", sa.Text(), nullable=True),
}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    with op.batch_alter_table("users") as batch_op:
        for name, column in NEW_COLUMNS.items():
            if name not in existing_columns:
                batch_op.add_column(column)
        for legacy_name in (
            "verification_code",
            "verification_code_expires_at",
            "verification_attempts",
        ):
            if legacy_name in existing_columns:
                batch_op.drop_column(legacy_name)

    existing_indexes = {index["name"] for index in sa.inspect(bind).get_indexes("users")}
    if "ix_users_email_verification_token_hash" not in existing_indexes:
        op.create_index(
            "ix_users_email_verification_token_hash",
            "users",
            ["email_verification_token_hash"],
            unique=False,
        )
    if "ix_users_password_reset_token_hash" not in existing_indexes:
        op.create_index(
            "ix_users_password_reset_token_hash",
            "users",
            ["password_reset_token_hash"],
            unique=False,
        )


def downgrade() -> None:
    raise RuntimeError("Authentication migration 0026 is intentionally irreversible")
