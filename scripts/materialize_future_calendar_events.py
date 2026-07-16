from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import date, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def backup_database(db_path: Path, label: str) -> str | None:
    if not db_path.exists():
        return None
    backup_dir = PROJECT_ROOT / "backups"
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"leverage_{label}_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    return str(backup_path.relative_to(PROJECT_ROOT))


def run(args: argparse.Namespace) -> dict:
    os.environ["DATABASE_URL"] = f"sqlite:///{args.db_path}"

    from app import models
    from app.calendar_import import (
        _build_event_lookup,
        _find_existing_events,
        infer_event_category,
        infer_event_discipline,
        infer_event_level,
        parse_calendar_file,
    )
    from app.database import SessionLocal

    rows, issues = parse_calendar_file(args.calendar_file.name, args.calendar_file.read_bytes())
    future_rows = [
        row for row in rows
        if row.year == args.year and row.start_date >= args.from_date
    ]

    db = SessionLocal()
    dry_run = not args.commit
    backup_path = None
    created_events: list[dict] = []
    existing_events: list[dict] = []
    calendar_entries: list[dict] = []
    ambiguous_rows: list[dict] = []
    try:
        lookup = _build_event_lookup(db, {args.year})
        if args.commit:
            backup_path = backup_database(args.db_path, f"future_calendar_{args.year}")

        for row in future_rows:
            matches = _find_existing_events(lookup, row)
            row_payload = {
                "calendar_row": row.row_number,
                "event_name": row.event_name,
                "start_date": row.start_date.isoformat(),
                "end_date": row.end_date.isoformat(),
            }
            if len(matches) > 1:
                ambiguous_rows.append({
                    **row_payload,
                    "matches": [{"id": event.id, "name": event.name} for event in matches],
                })
                continue

            if not matches:
                discipline = infer_event_discipline(row.event_name)
                category = infer_event_category(row.event_name)
                level = infer_event_level(row.event_name)
                detail = {
                    **row_payload,
                    "discipline": discipline.value,
                    "category": category.value,
                    "level": level.value,
                    "status": "created",
                }
                created_events.append(detail)
                if not dry_run:
                    event = models.Event(
                        name=row.event_name,
                        start_date=row.start_date,
                        end_date=row.end_date,
                        year=row.year,
                        discipline=discipline,
                        category=category,
                        level=level,
                    )
                    db.add(event)
                continue

            event = matches[0]
            if event.start_date == row.start_date and event.end_date == row.end_date:
                existing_events.append({
                    **row_payload,
                    "event_id": event.id,
                    "event_name": event.name,
                    "status": "already_present",
                })
                continue

            discipline = infer_event_discipline(row.event_name)
            source_note = (
                "future calendar row preserved as EventCalendarEntry; "
                "existing Event dates/results kept"
            )
            entry = db.query(models.EventCalendarEntry).filter(
                models.EventCalendarEntry.source == "gymternet_calendar",
                models.EventCalendarEntry.year == row.year,
                models.EventCalendarEntry.source_row == row.row_number,
                models.EventCalendarEntry.event_id == event.id,
                models.EventCalendarEntry.is_deleted.is_(False),
            ).first()
            detail = {
                **row_payload,
                "event_id": event.id,
                "matched_event_name": event.name,
                "matched_event_start_date": event.start_date.isoformat() if event.start_date else None,
                "matched_event_end_date": event.end_date.isoformat() if event.end_date else None,
                "discipline": discipline.value,
                "source_note": source_note,
            }
            if entry:
                changed = (
                    entry.name != row.event_name
                    or entry.start_date != row.start_date
                    or entry.end_date != row.end_date
                    or entry.discipline != discipline
                    or entry.source_note != source_note
                )
                detail["status"] = "updated" if changed else "already_present"
                detail["calendar_entry_id"] = entry.id
                if changed and not dry_run:
                    entry.name = row.event_name
                    entry.start_date = row.start_date
                    entry.end_date = row.end_date
                    entry.discipline = discipline
                    entry.source_note = source_note
            else:
                detail["status"] = "created"
                if not dry_run:
                    db.add(models.EventCalendarEntry(
                        event_id=event.id,
                        name=row.event_name,
                        start_date=row.start_date,
                        end_date=row.end_date,
                        year=row.year,
                        discipline=discipline,
                        source="gymternet_calendar",
                        source_row=row.row_number,
                        source_note=source_note,
                    ))
            calendar_entries.append(detail)

        if ambiguous_rows:
            db.rollback()
            committed = False
        elif args.commit:
            db.commit()
            committed = True
        else:
            db.rollback()
            committed = False

        summary = {
            "calendar_file": str(args.calendar_file),
            "database": str(args.db_path),
            "year": args.year,
            "from_date": args.from_date.isoformat(),
            "dry_run": dry_run,
            "committed": committed,
            "backup_path": backup_path,
            "source_issues": issues,
            "future_rows": len(future_rows),
            "created_events": len(created_events),
            "existing_events": len(existing_events),
            "calendar_entries": len(calendar_entries),
            "ambiguous_rows": len(ambiguous_rows),
            "created_event_details": created_events,
            "existing_event_details": existing_events,
            "calendar_entry_details": calendar_entries,
            "ambiguous_row_details": ambiguous_rows,
        }
    finally:
        db.close()

    args.report_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.report_dir / (
        f"calendar_{args.year}_future_materialization_"
        f"{'commit' if args.commit else 'dry_run'}_summary.json"
    )
    output_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    summary["output_path"] = str(output_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize future calendar rows as Events or calendar entries.")
    parser.add_argument("calendar_file", type=Path)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--from-date", type=date.fromisoformat, required=True)
    parser.add_argument("--db-path", type=Path, default=PROJECT_ROOT / "leverage.db")
    parser.add_argument("--report-dir", type=Path, default=PROJECT_ROOT / "docs" / "import_reports")
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps({
        "committed": summary["committed"],
        "future_rows": summary["future_rows"],
        "created_events": summary["created_events"],
        "existing_events": summary["existing_events"],
        "calendar_entries": summary["calendar_entries"],
        "ambiguous_rows": summary["ambiguous_rows"],
        "backup_path": summary["backup_path"],
        "output_path": summary["output_path"],
    }, indent=2))


if __name__ == "__main__":
    main()
