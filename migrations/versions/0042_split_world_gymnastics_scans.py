"""Separate athlete and event scan controls, keeping both paused on migration."""
from alembic import op
import sqlalchemy as sa

revision = "0042_split_wg_scans"
down_revision = "0041_world_gymnastics_scan"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("world_gymnastics_scan_control", sa.Column(
        "entity_type", sa.String(10), nullable=False, server_default="athlete"))
    op.create_index("uq_wg_scan_control_entity", "world_gymnastics_scan_control", ["entity_type"], unique=True)
    op.execute("""INSERT INTO world_gymnastics_scan_control
        (id, entity_type, enabled, started_at, athlete_cursor, event_cursor, consecutive_errors)
        SELECT 2, 'event', 0, started_at, 0, event_cursor, 0
        FROM world_gymnastics_scan_control WHERE id = 1""")
    op.execute("""UPDATE world_gymnastics_scan_control
        SET enabled = 0, lease_until = NULL, lease_token = NULL,
            consecutive_errors = 0, last_error = NULL""")
    op.execute("UPDATE world_gymnastics_scan_control SET event_cursor = 0 WHERE entity_type = 'athlete'")
    op.execute("UPDATE world_gymnastics_scan_jobs SET status = 'pending' WHERE status = 'running'")


def downgrade():
    op.execute("""UPDATE world_gymnastics_scan_control SET enabled = 0,
        event_cursor = COALESCE((SELECT event_cursor FROM world_gymnastics_scan_control WHERE id = 2), 0),
        lease_until = NULL, lease_token = NULL WHERE id = 1""")
    op.execute("DELETE FROM world_gymnastics_scan_control WHERE id = 2")
    op.drop_index("uq_wg_scan_control_entity", table_name="world_gymnastics_scan_control")
    with op.batch_alter_table("world_gymnastics_scan_control") as batch:
        batch.drop_column("entity_type")
