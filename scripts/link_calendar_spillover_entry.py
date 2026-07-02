from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import models
from app.calendar_import import infer_event_discipline, parse_calendar_file
from app.database import SessionLocal


def backup_database(db_path: Path, label: str) -> str | None:
    if not db_path.exists():
        return None
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"leverage_calendar_spillover_{label}_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    return str(backup_path)


def run(args: argparse.Namespace) -> dict:
    os.environ["DATABASE_URL"] = f"sqlite:///{args.db_path}"
    rows, issues = parse_calendar_file(args.calendar_file.name, args.calendar_file.read_bytes())
    calendar_row = next(
        (
            row
            for row in rows
            if row.year == args.calendar_year and row.row_number == args.calendar_row
        ),
        None,
    )
    if calendar_row is None:
        raise ValueError(f"Calendar row {args.calendar_year}:{args.calendar_row} was not found")

    db = SessionLocal()
    try:
        event = db.query(models.Event).filter(
            models.Event.id == args.event_id,
            models.Event.is_deleted.is_(False),
        ).first()
        if event is None:
            raise ValueError(f"Event {args.event_id} was not found")

        dry_run = not args.commit
        backup_path = None if dry_run else backup_database(args.db_path, f"{args.calendar_year}_{args.event_id}")
        note = args.note or (
            f"season_year_spillover: Calendar {args.calendar_year} row {args.calendar_row} "
            f"linked to Event {event.id} ({event.year}) after admin review"
        )

        updated_event_dates = False
        event_before = {
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
        }
        if event.start_date != calendar_row.start_date or event.end_date != calendar_row.end_date:
            if not event.start_date and not event.end_date:
                updated_event_dates = True
                if not dry_run:
                    event.start_date = calendar_row.start_date
                    event.end_date = calendar_row.end_date
            elif args.force_event_dates:
                updated_event_dates = True
                if not dry_run:
                    event.start_date = calendar_row.start_date
                    event.end_date = calendar_row.end_date
            else:
                raise ValueError(
                    f"Event {event.id} already has dates {event.start_date} - {event.end_date}; "
                    "rerun with --force-event-dates if this is intentional"
                )

        entry = db.query(models.EventCalendarEntry).filter(
            models.EventCalendarEntry.source == "gymternet_calendar",
            models.EventCalendarEntry.year == args.calendar_year,
            models.EventCalendarEntry.source_row == args.calendar_row,
            models.EventCalendarEntry.event_id == event.id,
            models.EventCalendarEntry.is_deleted.is_(False),
        ).first()

        entry_status = "updated" if entry else "created"
        if not dry_run:
            if entry is None:
                entry = models.EventCalendarEntry(
                    event_id=event.id,
                    name=calendar_row.event_name,
                    start_date=calendar_row.start_date,
                    end_date=calendar_row.end_date,
                    year=calendar_row.year,
                    discipline=infer_event_discipline(calendar_row.event_name),
                    source="gymternet_calendar",
                    source_row=calendar_row.row_number,
                    source_note=note,
                )
                db.add(entry)
            else:
                entry.name = calendar_row.event_name
                entry.start_date = calendar_row.start_date
                entry.end_date = calendar_row.end_date
                entry.discipline = infer_event_discipline(calendar_row.event_name)
                entry.source_note = note
            db.commit()
        else:
            db.rollback()

        return {
            "committed": not dry_run,
            "backup_path": backup_path,
            "source_issues": len(issues),
            "event": {
                "id": event.id,
                "name": event.name,
                "year": event.year,
                "discipline": event.discipline.value,
                "before": event_before,
                "after": {
                    "start_date": calendar_row.start_date.isoformat(),
                    "end_date": calendar_row.end_date.isoformat(),
                },
                "updated_dates": updated_event_dates,
            },
            "calendar_row": {
                "year": calendar_row.year,
                "row": calendar_row.row_number,
                "name": calendar_row.event_name,
                "date_label": calendar_row.date_label,
                "start_date": calendar_row.start_date.isoformat(),
                "end_date": calendar_row.end_date.isoformat(),
            },
            "calendar_entry": {
                "status": entry_status,
                "source_note": note,
            },
        }
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Link a Calendar source row to a cross-year Event as a season-year spillover."
    )
    parser.add_argument("calendar_file", type=Path)
    parser.add_argument("--calendar-year", type=int, required=True)
    parser.add_argument("--calendar-row", type=int, required=True)
    parser.add_argument("--event-id", type=int, required=True)
    parser.add_argument("--db-path", type=Path, default=Path("leverage.db"))
    parser.add_argument("--note", default="")
    parser.add_argument("--force-event-dates", action="store_true")
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    print(json.dumps(run(args), indent=2))


if __name__ == "__main__":
    main()
