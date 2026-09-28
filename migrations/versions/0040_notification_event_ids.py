"""Store distinct events in cumulative athlete notifications."""
from alembic import op
import sqlalchemy as sa

revision = "0040_notification_event_ids"
down_revision = "0039_repair_verified_athlete_audit"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("notifications")}
    if "related_event_ids" not in columns:
        op.add_column("notifications", sa.Column("related_event_ids", sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table("notifications") as batch:
        batch.drop_column("related_event_ids")
