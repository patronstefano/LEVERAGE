"""Local operator controls. Network processing is owned by the FastAPI worker."""
import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.audit import add_audit_log, model_snapshot
from app.database import engine, SessionLocal
from app.world_gymnastics_scan import get_control, scan_status, enqueue_initial


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--action", choices=["start", "pause", "status"], default="status")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.backup:
        path = Path("backups") / f"before_wg_scan_{datetime.now():%Y%m%d_%H%M%S}.db"
        path.parent.mkdir(exist_ok=True)
        with sqlite3.connect(engine.url.database) as source, sqlite3.connect(path) as target:
            source.backup(target)
        print(str(path))
        return
    with SessionLocal() as db:
        item = get_control(db)
        if args.action != "status":
            before = model_snapshot(item)
            item.enabled = args.action == "start"
            if item.started_at is None and args.action == "start":
                item.started_at = datetime.utcnow()
                enqueue_initial(db, item)
            add_audit_log(db, None, "update", "WorldGymnasticsScanControl", 1,
                          before=before, after=model_snapshot(item))
            db.commit()
        report = scan_status(db)
        text = json.dumps(report, default=str, indent=2)
        print(text)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(text + "\n")


if __name__ == "__main__":
    main()
