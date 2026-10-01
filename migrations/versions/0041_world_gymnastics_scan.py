"""Persist resumable World Gymnastics candidate searches, separate from certification."""
from alembic import op
import sqlalchemy as sa

revision = "0041_world_gymnastics_scan"
down_revision = "0040_notification_event_ids"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("world_gymnastics_scan_control",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("athlete_cursor", sa.Integer(), nullable=False),
        sa.Column("event_cursor", sa.Integer(), nullable=False),
        sa.Column("lease_until", sa.DateTime()),
        sa.Column("lease_token", sa.String(50)),
        sa.Column("consecutive_errors", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text()))
    op.create_table("world_gymnastics_scan_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(10), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("entity_name", sa.String(300), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("candidates", sa.JSON(), nullable=False),
        sa.Column("rejected_ids", sa.JSON(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("checked_at", sa.DateTime()),
        sa.Column("error", sa.Text()),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.UniqueConstraint("entity_type", "entity_id", name="uq_wg_scan_entity"))
    op.create_index("ix_wg_scan_status", "world_gymnastics_scan_jobs", ["status", "id"])


def downgrade():
    op.drop_table("world_gymnastics_scan_jobs")
    op.drop_table("world_gymnastics_scan_control")
