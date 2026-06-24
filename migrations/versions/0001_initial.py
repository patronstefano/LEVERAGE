"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("email_verification_token_hash", sa.String(length=64), nullable=True),
        sa.Column("email_verification_expires_at", sa.DateTime(), nullable=True),
        sa.Column("email_verification_sent_at", sa.DateTime(), nullable=True),
        sa.Column("password_reset_token_hash", sa.String(length=64), nullable=True),
        sa.Column("password_reset_expires_at", sa.DateTime(), nullable=True),
        sa.Column("password_reset_sent_at", sa.DateTime(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False),
        sa.Column("login_locked_until", sa.DateTime(), nullable=True),
        sa.Column("auth_version", sa.Integer(), nullable=False),
        sa.Column("mfa_secret", sa.String(length=64), nullable=True),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False),
        sa.Column("mfa_recovery_codes", sa.Text(), nullable=True),
        sa.Column("role", sa.Enum("ADMIN", "USER", name="roleenum"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email_verification_token_hash", "users", ["email_verification_token_hash"], unique=False)
    op.create_index("ix_users_password_reset_token_hash", "users", ["password_reset_token_hash"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "athletes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("birth_year", sa.Integer(), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("discipline", sa.Enum("MAG", "WAG", name="disciplineenum"), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "RETIRED", name="statusenum"), nullable=False),
        sa.Column("image_url", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "birth_year IS NULL OR (birth_year >= 1900 AND birth_year <= 2100)",
            name="ck_athletes_birth_year_valid",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_athletes_id"), "athletes", ["id"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("discipline", sa.Enum("MAG", "WAG", "BOTH", name="eventdisciplineenum"), nullable=False),
        sa.Column("category", sa.Enum("JUNIOR", "SENIOR", name="categoryenum"), nullable=False),
        sa.Column(
            "level",
            sa.Enum(
                "OLYMPIC_GAMES",
                "WORLD_CHAMPIONSHIPS",
                "CONTINENTAL_CHAMPIONSHIPS",
                "WORLD_CUP",
                "WORLD_CHALLENGE_CUP",
                "INTERNATIONAL_EVENT",
                "NATIONAL_EVENT",
                name="levelenum",
            ),
            nullable=False,
        ),
        sa.Column("image_url", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_id"), "events", ["id"], unique=False)

    op.create_table(
        "followed_athletes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("athlete_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "athlete_id", name="uq_followed_athletes_user_athlete"),
    )
    op.create_index(op.f("ix_followed_athletes_athlete_id"), "followed_athletes", ["athlete_id"], unique=False)
    op.create_index(op.f("ix_followed_athletes_id"), "followed_athletes", ["id"], unique=False)
    op.create_index(op.f("ix_followed_athletes_user_id"), "followed_athletes", ["user_id"], unique=False)

    op.create_table(
        "results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("athlete_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("discipline", sa.Enum("MAG", "WAG", name="disciplineenum"), nullable=False),
        sa.Column("apparatus", sa.String(length=50), nullable=True),
        sa.Column("vt_attempt", sa.Integer(), nullable=True),
        sa.Column("format", sa.Enum("TEAM", "INDIVIDUAL", "APPARATUS", name="formatenum"), nullable=False),
        sa.Column("round", sa.Enum("QUALIFICATION", "FINAL", name="roundenum"), nullable=False),
        sa.Column("D_score", sa.Float(), nullable=True),
        sa.Column("E_score", sa.Float(), nullable=True),
        sa.Column("Penalty", sa.Float(), nullable=True),
        sa.Column("Bonus", sa.Float(), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("Bonus IS NULL OR Bonus >= 0", name="ck_results_bonus_non_negative"),
        sa.CheckConstraint("D_score IS NULL OR D_score >= 0", name="ck_results_d_score_non_negative"),
        sa.CheckConstraint("E_score IS NULL OR E_score >= 0", name="ck_results_e_score_non_negative"),
        sa.CheckConstraint("Penalty IS NULL OR Penalty >= 0", name="ck_results_penalty_non_negative"),
        sa.CheckConstraint("score >= 0", name="ck_results_score_non_negative"),
        sa.CheckConstraint("vt_attempt IS NULL OR vt_attempt IN (1, 2)", name="ck_results_vt_attempt_valid"),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_results_id"), "results", ["id"], unique=False)

    op.create_table(
        "saved_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "event_id", name="uq_saved_events_user_event"),
    )
    op.create_index(op.f("ix_saved_events_event_id"), "saved_events", ["event_id"], unique=False)
    op.create_index(op.f("ix_saved_events_id"), "saved_events", ["id"], unique=False)
    op.create_index(op.f("ix_saved_events_user_id"), "saved_events", ["user_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.Enum("NEW_EVENT", "NEW_RESULT", name="notificationtypeenum"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("related_event_id", sa.Integer(), nullable=True),
        sa.Column("related_athlete_id", sa.Integer(), nullable=True),
        sa.Column("related_result_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["related_athlete_id"], ["athletes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["related_event_id"], ["events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["related_result_id"], ["results.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    op.create_table(
        "result_entry_contexts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("apparatus", sa.String(length=50), nullable=True),
        sa.Column("round", sa.Enum("QUALIFICATION", "FINAL", name="roundenum"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["admin_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "admin_id", name="uq_result_entry_context_event_admin"),
    )
    op.create_index(op.f("ix_result_entry_contexts_admin_id"), "result_entry_contexts", ["admin_id"], unique=False)
    op.create_index(op.f("ix_result_entry_contexts_event_id"), "result_entry_contexts", ["event_id"], unique=False)
    op.create_index(op.f("ix_result_entry_contexts_id"), "result_entry_contexts", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_result_entry_contexts_id"), table_name="result_entry_contexts")
    op.drop_index(op.f("ix_result_entry_contexts_event_id"), table_name="result_entry_contexts")
    op.drop_index(op.f("ix_result_entry_contexts_admin_id"), table_name="result_entry_contexts")
    op.drop_table("result_entry_contexts")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_saved_events_user_id"), table_name="saved_events")
    op.drop_index(op.f("ix_saved_events_id"), table_name="saved_events")
    op.drop_index(op.f("ix_saved_events_event_id"), table_name="saved_events")
    op.drop_table("saved_events")
    op.drop_index(op.f("ix_results_id"), table_name="results")
    op.drop_table("results")
    op.drop_index(op.f("ix_followed_athletes_user_id"), table_name="followed_athletes")
    op.drop_index(op.f("ix_followed_athletes_id"), table_name="followed_athletes")
    op.drop_index(op.f("ix_followed_athletes_athlete_id"), table_name="followed_athletes")
    op.drop_table("followed_athletes")
    op.drop_index(op.f("ix_events_id"), table_name="events")
    op.drop_table("events")
    op.drop_index(op.f("ix_athletes_id"), table_name="athletes")
    op.drop_table("athletes")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index("ix_users_password_reset_token_hash", table_name="users")
    op.drop_index("ix_users_email_verification_token_hash", table_name="users")
    op.drop_table("users")
