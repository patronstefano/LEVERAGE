"""Persist reviewed internal identity pairs independently of WG matches."""
from alembic import op
import sqlalchemy as sa

revision = "0043_entity_reviews"
down_revision = "0042_split_wg_scans"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("entity_review_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(10), nullable=False),
        sa.Column("left_id", sa.Integer(), nullable=False),
        sa.Column("right_id", sa.Integer(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("decision", sa.String(30), nullable=False),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("entity_type", "left_id", "right_id", "fingerprint", name="uq_entity_review_pair"),
        sa.CheckConstraint("left_id < right_id", name="ck_entity_review_pair_order"))


def downgrade():
    op.drop_table("entity_review_decisions")
